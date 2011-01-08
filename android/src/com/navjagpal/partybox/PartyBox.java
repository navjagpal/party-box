package com.navjagpal.partybox;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import android.accounts.Account;
import android.accounts.AccountManager;
import android.accounts.AccountManagerCallback;
import android.accounts.AccountManagerFuture;
import android.accounts.AuthenticatorException;
import android.accounts.OperationCanceledException;
import android.app.Activity;
import android.app.ListActivity;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.widget.ListAdapter;
import android.widget.SimpleAdapter;

public class PartyBox extends ListActivity {
	
    protected static final String LTAG = "PartyBox";
    private static final String SERVER = new String("http://party-box.appspot.com");
    private PartyBoxClient mClient;

	/** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Grab an auth token for GAE.
        AccountManager accountManager = AccountManager.get(this);
        Account[] accounts = accountManager.getAccountsByType("com.google");
        
        // TODO(nav): Use first account by default, but we should give the user an option.
        Account account = accounts[0];
        AccountManagerCallback<Bundle> callback = new AccountManagerCallback<Bundle>() {
			@Override
			public void run(AccountManagerFuture<Bundle> bundle) {
				try {
					String authToken = bundle.getResult().get(
							AccountManager.KEY_AUTHTOKEN).toString();
					Log.i(LTAG, "Account manager callback with token " + authToken);
							
					//mClient = new PartyBoxClient(Uri.parse(SERVER), authToken);
					mClient = new TestingPartyBoxClient(Uri.parse(SERVER), authToken);
					displayPlaylist();
				} catch (OperationCanceledException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				} catch (AuthenticatorException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
        	
        };
        accountManager.getAuthToken(
        		account, "ah", null, this, callback, null);
    }
    
    private void displayPlaylist() {
    	new GetPlaylistTask().execute();
    }
    
    private class GetPlaylistTask extends AsyncTask<Void, Void, ArrayList<HashMap<String, String>>> {

		@Override
		protected ArrayList<HashMap<String, String>> doInBackground(Void... arg0) {
			List<Song> songs = mClient.GetPlaylist();
	    	ArrayList<HashMap<String, String>> data = new ArrayList<HashMap<String, String>>();
	    	for (Song song : songs) {
	    		HashMap<String, String> row = new HashMap<String, String>();
	    		row.put("id", song.id);
	    		row.put("title", song.title);
	    		data.add(row);
	    	}
	    	return data;
		}
		
		@Override
		protected void onPostExecute(ArrayList<HashMap<String, String>> result) {
			ListAdapter adapter = new SimpleAdapter(
	    			PartyBox.this, result, android.R.layout.two_line_list_item,
	    			new String[] { "id", "title" },
	    			new int[] { android.R.id.text1, android.R.id.text2 });
	    	setListAdapter(adapter);
		}
    	
    }
}