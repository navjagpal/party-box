package com.navjagpal.partybox;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;

public class PartyBox extends Activity {
	
    protected static final String LTAG = "PartyBox";
    
    /** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);

        Button playlistButton = (Button) findViewById(R.id.playlistButton);
        playlistButton.setOnClickListener(new OnClickListener() {
			@Override
			public void onClick(View view) {
				Intent intent = new Intent();
				intent.setClassName("com.navjagpal.partybox", "com.navjagpal.partybox.PlaylistActivity");
				startActivity(intent);
			}
        });
    }

}
