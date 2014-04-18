package net.nature.api.test;

import static com.jayway.restassured.RestAssured.get;
import static org.hamcrest.Matchers.*;

import org.junit.Before;
import org.junit.Test;

import com.jayway.restassured.RestAssured;

public class SiteTest {

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
	public void  get_all_contexts_for_site() {
		get("/site/test/contexts")
		.then()
		.body("data.id", everyItem(equalTo(1)));
	}

	
}