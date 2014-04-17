package net.nature.api.test;

import static com.jayway.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;

import java.util.HashSet;
import java.util.Set;

import org.junit.Before;
import org.junit.Test;

import com.jayway.restassured.RestAssured;

public class AccountTest {
	
	// class variable
	final String lexicon = "ABCDEFGHIJKLMNOPQRSTUVWXYZ12345674890";

	final java.util.Random rand = new java.util.Random();

	// consider using a Map<String,Boolean> to say whether the identifier is being used or not 
	final Set<String> identifiers = new HashSet<String>();

	public String randomIdentifier() {
	    StringBuilder builder = new StringBuilder();
	    while(builder.toString().length() == 0) {
	        int length = rand.nextInt(5)+5;
	        for(int i = 0; i < length; i++)
	            builder.append(lexicon.charAt(rand.nextInt(lexicon.length())));
	        if(identifiers.contains(builder.toString())) 
	            builder = new StringBuilder();
	    }
	    return builder.toString();
	}
	
	
	@Before
	public void setUp(){
		RestAssured.baseURI = "http://localhost";
		RestAssured.port = 5000;
		RestAssured.basePath = "/api";
	}
	
	@Test
	public void  count() {
		get("/accounts/count")
		.then()
			.body("data", greaterThan(5));
	}  

	@Test
	public void  get_tomyeh() {
		get("/account/tomyeh")
		.then()
		.body("data.username", equalTo("tomyeh"));
	}
	
	@Test
	public void  create_new() {
		String newname = randomIdentifier();
		post("/account/new/" + newname).
			then().
			body("data.username", equalTo(newname));
	}

	@Test
	public void  error_create_new_username_already_taken() {
		post("/account/new/tomyeh").
			then().
			statusCode(400);
	}	

	
	@Test
	public void  get_abby() {
		get("/account/abby")
		.then()
		.body("data.username", equalTo("abby"));
	}  

	@Test
	public void  get_all_accounts() {
		get("/accounts")
		.then()
		.body("data.username", hasItems("tomyeh","abby"));		
	}  

	@Test
	public void  get_notes_for_tomyeh() {
		get("/account/tomyeh/notes").
			then().
			body("data.content", hasItems("first note taken by tomyeh")).
			body("data.account.username", everyItem(equalTo("tomyeh")));
	}  
	
}