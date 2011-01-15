package com.navjagpal.partybox;

import java.io.IOException;
import java.io.InputStream;
import java.util.LinkedList;
import java.util.List;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.params.ClientPNames;
import org.apache.http.impl.client.DefaultHttpClient;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.net.Uri;
import android.util.Log;

public class PartyBoxClient {
	
	private static final Uri SERVER_URI = Uri.parse("https://party-box.appspot.com");

	private String mAuthToken;
	private DefaultHttpClient mHttpClient;
	private boolean mAuthenticated;
	
	public PartyBoxClient(String authToken) {
		mHttpClient = new DefaultHttpClient();
		mAuthToken = authToken;
		mAuthenticated = false;
	}
	
	private void authenticate() {
		// TODO(nav): Store auth cookies.
		HttpGet get = new HttpGet(SERVER_URI.buildUpon().
				appendPath("_ah").
				appendPath("login").
				appendQueryParameter(
						"continue", "http://localhost/").
				appendQueryParameter(
						"auth", mAuthToken).toString());
		try {
			mHttpClient.getParams().setBooleanParameter(ClientPNames.HANDLE_REDIRECTS, false);
			HttpResponse response = mHttpClient.execute(get);
			HttpEntity entity = response.getEntity();
			Log.i(PartyBox.LTAG, "Get response: " + response.getStatusLine());
			entity.consumeContent();
			mAuthenticated = true; // TODO(nav): Should check that auth really worked.
		} catch (ClientProtocolException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} finally {
			mHttpClient.getParams().setBooleanParameter(ClientPNames.HANDLE_REDIRECTS, true);
		}
	}
	
	private String makeRequest(Uri uri) {
		String result = null;
		HttpGet get = new HttpGet(uri.toString());
		HttpResponse response;
		try {
			response = mHttpClient.execute(get);
			HttpEntity entity = response.getEntity();
			Log.i(PartyBox.LTAG, "Get response: " + response.getStatusLine());
			byte[] b = new byte[4096];
			InputStream in = entity.getContent();
			StringBuffer out = new StringBuffer();
			for (int n; (n = in.read(b)) != -1;) {
		        out.append(new String(b, 0, n));
		    }
			result = out.toString();
		} catch (ClientProtocolException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return result;
	}
	
	public List<Song> GetPlaylist() {
		if (!mAuthenticated)
			authenticate();
		
		List<Song> playlist = new LinkedList<Song>();
		try {
			String result = makeRequest(SERVER_URI.buildUpon()
					.appendPath("youtube")
					.appendPath("playlist").build());
			Log.i(PartyBox.LTAG, "Raw resposne = " + result);
			JSONArray json = new JSONArray(result);
			Log.i(PartyBox.LTAG, "JSon = " + json.toString());
			
			if (json != null) {
				for (int i = 0; i < json.length(); i++) {
					Song song = new Song();
					JSONObject entry = json.getJSONObject(i);
					song.id = entry.getString("id");
					song.title = entry.getString("title");
					song.count = entry.getInt("count");
					song.voted = entry.getBoolean("voted");
					JSONArray thumbnails = entry.getJSONArray("thumbnails");
					for (int j = 0; j < thumbnails.length(); j++) {
						song.thumbnails.add(thumbnails.getString(j));
					}
					playlist.add(song);
				}
			}
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		return playlist;
	}
	
	public Song vote(Song song) {
		if (!mAuthenticated)
			authenticate();
		
		try {
			Uri.Builder builder = SERVER_URI.buildUpon()
				.appendPath("youtube")
				.appendPath("add")
				.appendQueryParameter("id", song.id)
				.appendQueryParameter("title", song.title);
			
			for (String thumbnail : song.thumbnails) {
				builder.appendQueryParameter("thumbnail", thumbnail);
			}
			
			Log.i(PartyBox.LTAG, "Voting URL: " + builder.toString());
			String result = makeRequest(builder.build());
			Log.i(PartyBox.LTAG, "Raw response = " + result);
			JSONObject json = new JSONObject(result);
			Log.i(PartyBox.LTAG, "JSon = " + json.toString());
			
			if (json != null) {
				JSONObject entry = json.getJSONObject("entry");
				Song updatedSong = new Song();
				updatedSong.id = entry.getString("id");
				updatedSong.title = entry.getString("title");
				updatedSong.voted = entry.getBoolean("voted");
				return updatedSong;
			}
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		return null;
	}

	public List<Song> Search(String query) {
		// TODO(nav): Replace this search by searching YouTube directly. Contacting
		// the party box service for the search has some overhead for SSL, the authentication,
		// and it imposes extra load on our appengine app.
		if (!mAuthenticated)
			authenticate();
		
		Uri.Builder builder = SERVER_URI.buildUpon()
		.appendPath("youtube").appendPath("search")
		.appendQueryParameter("q", query);
	
		List<Song> searchResults = new LinkedList<Song>();
		try {
			String result = makeRequest(builder.build());
			Log.i(PartyBox.LTAG, "Raw response = " + result);
			JSONArray json = new JSONArray(result);
			Log.i(PartyBox.LTAG, "JSon = " + json.toString());
			
			if (json != null) {
				for (int i = 0; i < json.length(); i++) {
					Song song = new Song();
					JSONObject entry = json.getJSONObject(i);
					song.id = entry.getString("id");
					song.title = entry.getString("title");
					JSONArray thumbnails = entry.getJSONArray("thumbnails");
					for (int j = 0; j < thumbnails.length(); j++) {
						song.thumbnails.add(thumbnails.getString(j));
					}
					searchResults.add(song);
				}
			}
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		return searchResults;
	}
	

}
