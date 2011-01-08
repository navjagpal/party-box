package com.navjagpal.partybox;

import java.io.IOException;
import java.util.List;

import android.accounts.Account;
import android.accounts.AccountManager;
import android.accounts.AccountManagerCallback;
import android.accounts.AccountManagerFuture;
import android.accounts.AuthenticatorException;
import android.accounts.OperationCanceledException;
import android.app.ListActivity;
import android.content.Context;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;

public class PlaylistActivity extends ListActivity {
	
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
					Log.i(PartyBox.LTAG, "Account manager callback with token " + authToken);
							
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
    
    @Override
    protected void onListItemClick(ListView l, View v, int position, long id) {
    	Song song = (Song) l.getItemAtPosition(position);
    	Log.i(PartyBox.LTAG, "Song clicked " + song.title);
    }
    
    private void displayPlaylist() {
    	new GetPlaylistTask().execute();
    }
    

    private class GetPlaylistTask extends AsyncTask<Void, Void, List<Song>> {

		@Override
		protected List<Song> doInBackground(Void... arg0) {
			// This is a potentially expensive operation because it involves
			// the network, that's why we do it in the background.
			List<Song> songs = mClient.GetPlaylist();
	    	return songs;
		}
		
		@Override
		protected void onPostExecute(List<Song> playlist) {
			PlaylistAdapter adapter = new PlaylistAdapter(
					PlaylistActivity.this, playlist);
	    	setListAdapter(adapter);
		}
    }
    
    private class PlaylistAdapter extends BaseAdapter {
    	
    	private Context mContext;
    	private List<Song> mPlaylist;
    	
    	public PlaylistAdapter(Context context, List<Song> playlist) {
    		mContext = context;
    		mPlaylist = playlist;
    	}

		@Override
		public int getCount() {
			return mPlaylist.size();
		}

		@Override
		public Object getItem(int position) {
			return mPlaylist.get(position);
		}

		@Override
		public long getItemId(int position) {
			return position;
		}

		@Override
		public View getView(int position, View convertView, ViewGroup parent) {
			SongView sv;
			if (convertView == null) {
				sv = new SongView(mContext, mPlaylist.get(position));
			} else {
				sv = (SongView) convertView;
				sv.setSong(mPlaylist.get(position));
			}
			return sv;
		}
    }
    
    private class SongView extends LinearLayout {
    	private TextView mTitleView;
    	public SongView(Context context, Song song) {
    		super(context);
    		LayoutInflater layoutInflater = (LayoutInflater) context.getSystemService(
    				Context.LAYOUT_INFLATER_SERVICE);
    		  
    		layoutInflater.inflate(R.layout.song, this);

    		mTitleView = (TextView) findViewById(R.id.title);
    		setSong(song);
    	}
    	
    	public void setSong(Song song) {
    		mTitleView.setText(song.title);
    	}
    }
}