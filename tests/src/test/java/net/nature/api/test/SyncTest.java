package net.nature.api.test;

import static com.jayway.restassured.RestAssured.get;
import static org.hamcrest.Matchers.*;

import org.junit.Before;
import org.junit.Test;

import com.jayway.restassured.RestAssured;

public class SyncTest {

	@Before
	public void setUp(){
		RestAssured.baseURI = "http://localhost";
		RestAssured.port = 5000;
		RestAssured.basePath = "/api";
	}
	
	@Test
	public void  get_single_site() {
		get("/site/test")
		.then()
		.body("data.name", equalTo("test"));
	}
	
	@Test
	public void  get_all_sites() {
		get("/sites")
		.then()
		.body("data.name", hasItems("test","cu","umd"));
	}
	
	@Test
	public void  get_accounts_created_since() {
		get("/sync/accounts/created/since/2014/3/5/0/0").
		then().
		body("data.username", not(hasItems("tomyeh"))).
		body("data.username", hasItems("matt"));
	}
	
	@Test
	public void  get_accounts_created_recent() {
		get("/sync/accounts/created/recent/5").
		then().
		body("data.username", not(hasItems("tomyeh"))).
		body("data.username", hasSize(5));		
	}
	

	@Test
	public void  get_notes_created_since() {
		get("/sync/accounts/created/since/2014/4/1/4/10").
		then().
		body("data.id", everyItem(greaterThan(50)));
	}
	
	@Test
	public void  get_notes_created_recent() {
		get("/sync/notes/created/recent/5").
		then().
		body("data.id", everyItem(greaterThan(20))).
		body("data.id", hasSize(5));		
	}

	@Test
	public void  get_notes_created_later() {
		get("/sync/notes/created/recent/5").
		then().
		body("data.id", everyItem(greaterThan(20))).
		body("data.id", hasSize(5));		
	}

	
}