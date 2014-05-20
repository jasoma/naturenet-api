package net.nature.api.test;

import static com.jayway.restassured.RestAssured.get;
import static com.jayway.restassured.RestAssured.given;
import static org.hamcrest.Matchers.*;

import org.junit.Before;
import org.junit.Test;

import com.jayway.restassured.RestAssured;

public class NoteTest {
	
	@Before
	public void setUp(){
		RestAssured.baseURI = "http://localhost";
		RestAssured.port = 5000;
		RestAssured.basePath = "/api";
	}

	@Test
	public void  get_single_note() {
		get("/note/1")
		.then()
			.body("data.kind", equalTo("FieldNote"));
	}

	@Test
	public void  create_succeed() {
		given().
	 		param("content", "new note").
	 		param("context", "cu_tree").
	 		param("kind", "FieldNote").
	 		param("latitude", -33.4304234).
	 		param("longitude", 153.232431).
	 	when().
	 		post("/note/new/tomyeh").
	 	then().
	 		body("data.kind", equalTo("FieldNote")).
	 		body("data.content", equalTo("new note")).
	 		body("data.context.name", equalTo("cu_tree")).
	 		body("data.account.username", equalTo("tomyeh")).
	 		body("data.latitude", equalTo(-33.4304234f)).
			body("data.longitude", equalTo(153.232431f));
	}
	
	@Test
	public void  update_content_and_context() {
		given().
			param("username", "tomyeh").
	 		param("content", "new note content").
	 		param("context", "cu_building").
	 	when().
	 		post("/note/1/update").
	 	then().
	 		body("data.kind", equalTo("FieldNote")).
	 		body("data.content", equalTo("new note content")).
	 		body("data.context.name", equalTo("cu_building"));
	}
	
	@Test
	public void  error_update_bad_context() {
		given().
			param("username", "tomyeh").
	 		param("context", "bad_bad_context").
	 	when().
	 		post("/note/1/update").
	 	then().
	 		statusCode(400);
	}

	@Test
	public void  error_create_without_enough_parameters(){
		given(). 		
		when().
 			post("/note/new/tomyeh").
 		then().
	 		statusCode(400);
	}  
	
	@Test
	public void  error_create_username_does_not_exist(){
		given(). 		
		when().
 			post("/note/new/blahblahxxxxx123").
 		then().
	 		statusCode(400);
	}  
}