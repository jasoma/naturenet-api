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
	public void  get_accounts_since_date() {
		get("/sync/accounts/since/2014/3/5/0/0").
		then().
		body("data.username", not(hasItems("tomyeh"))).
		body("data.username", hasItems("matt"));
	}

	
}