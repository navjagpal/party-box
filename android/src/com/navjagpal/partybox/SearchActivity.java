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
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Log;
import android.view.ContextMenu;
import android.view.LayoutInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.BaseAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;

public class SearchActivity extends ListActivity {
	
	private static final int MENU_ADD = 0;
	private PartyBoxClient mClient;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.search);
		
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
		
		Button searchButton = (Button) findViewById(R.id.searchButton);
		searchButton.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View v) {
				EditText queryInput = (EditText) findViewById(R.id.query);
				Log.i(PartyBox.LTAG, "Searching " + queryInput.getText().toString());
				new SearchTask().execute(queryInput.getText().toString());
			}
		});
		
		 // Inform the list we provide context menus for items
        getListView().setOnCreateContextMenuListener(this);
	}
	
	@Override
	public void onCreateContextMenu(ContextMenu menu, View v, ContextMenu.ContextMenuInfo menuInfo) {
		menu.add(0, MENU_ADD, 0, R.string.add);
	}
	
	@Override
    public boolean onContextItemSelected(MenuItem item) {
      AdapterView.AdapterContextMenuInfo info;
      info = (AdapterView.AdapterContextMenuInfo) item.getMenuInfo();
    
      switch (item.getItemId()) {
      case MENU_ADD:
    	  Song song = (Song) getListAdapter().getItem(info.position);
    	  new VoteTask().execute(song);
    	  return true;    	  
      }
      
      return false;
    }
	
	private class SearchTask extends AsyncTask<String, Void, List<Song>> {
		@Override
    	protected void onPreExecute() {
    		ProgressBar progressBar = (ProgressBar) findViewById(R.id.progressBar);
    		progressBar.setVisibility(View.VISIBLE);
    	}
		
		@Override
		protected List<Song> doInBackground(String... queries) {
			return mClient.Search(queries[0]);
		}
		
		@Override
		protected void onPostExecute(List<Song> results) {
			ProgressBar progressBar = (ProgressBar) findViewById(R.id.progressBar);
    		progressBar.setVisibility(View.GONE);
			SearchResultsAdapter adapter = new SearchResultsAdapter(
					SearchActivity.this, results);
			setListAdapter(adapter);
		}
	}
	
	private class VoteTask extends AsyncTask<Song, Void, Void> {
		@Override
		// TODO(nav): Display results back to the user, some sort of feedback.
		protected Void doInBackground(Song... songs) {
			for (Song song : songs) {
				mClient.vote(song);
			}
			return null;
		}
    }
	
	private class SearchResultsAdapter extends BaseAdapter {
		
		private Context mContext;
		private List<Song> mSearchResults;
		
		public SearchResultsAdapter(Context context, List<Song> searchResults) {
			mContext = context;
			mSearchResults = searchResults;
		}

		@Override
		public int getCount() {
			return mSearchResults.size();
		}

		@Override
		public Object getItem(int position) {
			return mSearchResults.get(position);
		}

		@Override
		public long getItemId(int position) {
			return position;
		}

		@Override
		public View getView(int position, View convertView, ViewGroup parent) {
			SongView sv;
			if (convertView == null) {
				sv = new SongView(mContext, mSearchResults.get(position));
			} else {
				sv = (SongView) convertView;
				sv.setSong(mSearchResults.get(position));
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
    		  
    		layoutInflater.inflate(R.layout.search_result, this);
    		mTitleView = (TextView) findViewById(R.id.title);
    		setSong(song);
		}
		
		public void setSong(Song song) {
			mTitleView.setText(song.title);
			if (song.thumbnailImages.size() > 0) {
    			ImageView thumbnailImage = (ImageView) findViewById(R.id.thumbnail);
    			thumbnailImage.setImageBitmap(song.thumbnailImages.get(0));
    		}
		}
		
	}

}
