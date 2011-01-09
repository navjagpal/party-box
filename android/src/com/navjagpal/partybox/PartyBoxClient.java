package com.navjagpal.partybox;

import java.io.IOException;
import java.io.InputStream;
import java.net.URLEncoder;
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
	
	private Uri mServer;
	private String mAuthToken;
	private DefaultHttpClient mHttpClient;
	private boolean mAuthenticated;
	
	public PartyBoxClient(Uri server, String authToken) {
		mHttpClient = new DefaultHttpClient();
		mServer = server;
		mAuthToken = authToken;
		mAuthenticated = false;
	}
	
	private void authenticate() {
		// TODO(nav): Store auth cookies.
		HttpGet get = new HttpGet(
				"https://party-box.appspot.com/_ah/login?continue=" +
				"http://localhost/&auth=" + mAuthToken);
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
	
	public List<Song> GetPlaylist() {
		if (!mAuthenticated)
			authenticate();
		HttpGet get = new HttpGet("https://party-box.appspot.com/youtube/playlist");
		HttpResponse response;
		List<Song> playlist = new LinkedList<Song>();
		try {
			response = mHttpClient.execute(get);
			HttpEntity entity = response.getEntity();
			Log.i(PartyBox.LTAG, "Get response: " + response.getStatusLine());
			StringBuffer out = new StringBuffer();
			byte[] b = new byte[4096];
			InputStream in = entity.getContent();
			for (int n; (n = in.read(b)) != -1;) {
		        out.append(new String(b, 0, n));
		    }
			Log.i(PartyBox.LTAG, "Raw resposne = " + out.toString());
			JSONArray json = new JSONArray(out.toString());
			Log.i(PartyBox.LTAG, "JSon = " + json.toString());
			
			if (json != null) {
				for (int i = 0; i < json.length(); i++) {
					Song song = new Song();
					JSONObject entry = json.getJSONObject(i);
					song.id = entry.getString("id");
					song.title = entry.getString("title");
					song.count = entry.getInt("count");
					song.voted = entry.getBoolean("voted");
					playlist.add(song);
				}
			}
		} catch (ClientProtocolException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
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
			String query = "id=" + song.id + "&title=" +
			URLEncoder.encode(song.title, "utf8");
			for (String thumbnail : song.thumbnails) {
				query += "&thumbnail=" + URLEncoder.encode(thumbnail, "utf8");
			}
			HttpGet get = new HttpGet("https://party-box.appspot.com/youtube/add?" + query);
			HttpResponse response;
			response = mHttpClient.execute(get);
			HttpEntity entity = response.getEntity();
			Log.i(PartyBox.LTAG, "Get response: " + response.getStatusLine());
			StringBuffer out = new StringBuffer();
			byte[] b = new byte[4096];
			InputStream in = entity.getContent();
			for (int n; (n = in.read(b)) != -1;) {
		        out.append(new String(b, 0, n));
		    }
			Log.i(PartyBox.LTAG, "Raw resposne = " + out.toString());
			JSONObject json = new JSONObject(out.toString());
			Log.i(PartyBox.LTAG, "JSon = " + json.toString());
			
			if (json != null) {
				JSONObject entry = json.getJSONObject("entry");
				Song updatedSong = new Song();
				updatedSong.id = entry.getString("id");
				updatedSong.title = entry.getString("title");
				updatedSong.voted = entry.getBoolean("voted");
				return updatedSong;
			}
		} catch (ClientProtocolException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		return null;
	}
	

}
