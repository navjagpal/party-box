package com.navjagpal.partybox;

import java.util.LinkedList;
import java.util.List;

import android.util.Log;

public class TestingPartyBoxClient extends PartyBoxClient {
	
	public TestingPartyBoxClient(String authToken) {
		super(authToken);
	}
	
	public List<Song> GetPlaylist() {
		List<Song> playlist = new LinkedList<Song>();
		Song song1 = new Song();
		song1.id = "sOnqjkJTMaA";
		song1.title = "Thriller";
		song1.count = 5;
		playlist.add(song1);
		Song song2 = new Song();
		song2.id = "BBB";
		song2.title = "Beat It";
		song2.count = 3;
		playlist.add(song2);
		return playlist;
	}
	
	public Song vote(Song song) {
		Song newSong = new Song();
		newSong.id = song.id;
		newSong.title = song.title;
		newSong.thumbnails = song.thumbnails;
		newSong.count = song.count + 1;
		newSong.voted = true;
		Log.i(PartyBox.LTAG, "Voting on song " + song.title);
		return newSong;
	}

}
