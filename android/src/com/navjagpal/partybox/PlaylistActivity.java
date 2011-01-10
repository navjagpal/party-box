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
import android.content.Intent;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.ContextMenu;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.BaseAdapter;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.TextView;

public class PlaylistActivity extends ListActivity {
	
	private static final int MENU_PLAY = 0;
    private PartyBoxClient mClient;

	/** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.playlist);
              
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
							
					mClient = new PartyBoxClient(authToken);
					//mClient = new TestingPartyBoxClient(authToken);
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
        
        // Inform the list we provide context menus for items
        getListView().setOnCreateContextMenuListener(this);
    }
    
    @Override
    protected void onListItemClick(ListView l, View v, int position, long id) {
    	Song song = (Song) l.getItemAtPosition(position);
    	if (!song.voted) { 
    		new VoteTask().execute(song);
    	}
    }
    
    @Override
	public boolean onCreateOptionsMenu(Menu menu) {
        MenuInflater inflater = getMenuInflater();
        inflater.inflate(R.menu.playlist_options_menu, menu);
        return true;
    }
    
    @Override
    public void onCreateContextMenu(ContextMenu menu, View v, ContextMenu.ContextMenuInfo menuInfo) {
    	menu.add(0, MENU_PLAY, 0, R.string.play);
    }
    
    @Override
    public boolean onContextItemSelected(MenuItem item) {
      AdapterView.AdapterContextMenuInfo info;
      info = (AdapterView.AdapterContextMenuInfo) item.getMenuInfo();
    
      switch (item.getItemId()) {
      case MENU_PLAY:
    	  Song song = (Song) getListAdapter().getItem(info.position);
    	  startActivity(new Intent(Intent.ACTION_VIEW,
    			  Uri.parse("http://www.youtube.com/watch?v=" + song.id)));
    	  return true;
      }
      
      return false;
    }
      
      
    
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle item selection
        switch (item.getItemId()) {
        case R.id.refresh:
        	new GetPlaylistTask().execute();
        	return true;
        }
        return false;
    }
    
    private void displayPlaylist() {
    	new GetPlaylistTask().execute();
    }
    

    private class GetPlaylistTask extends AsyncTask<Void, Void, List<Song>> {
    	
    	@Override
    	protected void onPreExecute() {
    		ProgressBar progressBar = (ProgressBar) findViewById(R.id.progressBar);
    		progressBar.setVisibility(View.VISIBLE);
    	}

		@Override
		protected List<Song> doInBackground(Void... arg0) {
			// This is a potentially expensive operation because it involves
			// the network, that's why we do it in the background.
			List<Song> songs = mClient.GetPlaylist();
	    	return songs;
		}
		
		@Override
		protected void onPostExecute(List<Song> playlist) {
			ProgressBar progressBar = (ProgressBar) findViewById(R.id.progressBar);
    		progressBar.setVisibility(View.GONE);
			PlaylistAdapter adapter = new PlaylistAdapter(
					PlaylistActivity.this, playlist);
	    	setListAdapter(adapter);
		}
    }
    
    private class VoteTask extends AsyncTask<Song, Song, Void> {

		@Override
		protected Void doInBackground(Song... songs) {
			for (Song song : songs) {
				Song newSong = mClient.vote(song);
				if (newSong != null) {
					publishProgress(newSong);
				}
			}
			return null;
		}
		
		@Override
		protected void onProgressUpdate(Song... songs)  {
			PlaylistAdapter adapter = (PlaylistAdapter) getListAdapter();
			for (Song song : songs) {
				adapter.updateSong(song);
			}
		}
    	
    }
    
    private class PlaylistAdapter extends BaseAdapter {
    	
    	private Context mContext;
    	private List<Song> mPlaylist;
    	
    	public PlaylistAdapter(Context context, List<Song> playlist) {
    		mContext = context;
    		mPlaylist = playlist;
    	}

		public void updateSong(Song newSong) {
			for (Song song : mPlaylist) {
				if (song.id == newSong.id) {
					song.count = newSong.count;
					song.voted = newSong.voted;
					notifyDataSetChanged();
				}
			}
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
    	private TextView mCountView;
    	
    	public SongView(Context context, Song song) {
    		super(context);
    		
    		LayoutInflater layoutInflater = (LayoutInflater) context.getSystemService(
    				Context.LAYOUT_INFLATER_SERVICE);
    		  
    		layoutInflater.inflate(R.layout.song, this);

    		mTitleView = (TextView) findViewById(R.id.title);
    		mCountView = (TextView) findViewById(R.id.count);
    		setSong(song);
    	}
    	
    	public void setSong(Song song) {
    		mTitleView.setText(song.title);
    		mCountView.setText(String.valueOf(song.count));
			
    		ImageView statusImage = (ImageView) findViewById(R.id.statusImage);
    		if (song.voted) {
    			statusImage.setImageResource(R.drawable.voted);
    		} else {
    			statusImage.setImageResource(R.drawable.thumbsup);
    		}
    	}
    }
}