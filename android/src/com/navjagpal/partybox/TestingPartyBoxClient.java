package com.navjagpal.partybox;

import java.util.LinkedList;
import java.util.List;

import android.net.Uri;

public class TestingPartyBoxClient extends PartyBoxClient {
	
	public TestingPartyBoxClient(Uri server, String authToken) {
		super(server, authToken);
	}
	
	public List<Song> GetPlaylist() {
		List<Song> playlist = new LinkedList<Song>();
		Song song1 = new Song();
		song1.id = "AAA";
		song1.title = "Thriller";
		playlist.add(song1);
		Song song2 = new Song();
		song2.id = "BBB";
		song2.title = "Beat It";
		playlist.add(song2);
		return playlist;
	}

}
