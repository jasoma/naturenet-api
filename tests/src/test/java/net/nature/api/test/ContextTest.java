package net.nature.api.test;

import static com.jayway.restassured.RestAssured.get;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.everyItem;

import org.junit.Before;
import org.junit.Test;

import com.jayway.restassured.RestAssured;

public class ContextTest {

	@Before
	public void setUp(){
		RestAssured.baseURI = "http://localhost";
		RestAssured.port = 5000;
		RestAssured.basePath = "/api";
	}
	
	@Test
	public void  get_single_note() {
		get("/context/1").then().body("context.kind", equalTo("Activity"))
			.and().body("context.name", equalTo("ask"));
	}
	
	@Test
	public void  get_notes() {
		get("/context/1/notes").then().body("notes.context.id", everyItem(equalTo(1)));
	}

	@Test
	public void  get_all_activities() {
		get("/context/activities").then().body("contexts.kind", everyItem(equalTo("Activity")));
	}


	@Test
	public void  get_all_landmarks() {
		get("/context/landmarks").then().body("contexts.kind", everyItem(equalTo("Landmark")));
	}

}