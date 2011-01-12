package com.navjagpal.partybox;

import java.util.LinkedList;
import java.util.List;

import android.graphics.Bitmap;

public class Song {
	
	public String id;
	public String title;
	public int count;
	public boolean voted = false;
	public List<String> thumbnails;
	public List<Bitmap> thumbnailImages;
	
	public Song() {
		thumbnails = new LinkedList<String>();
		thumbnailImages = new LinkedList<Bitmap>();
	}

}
