package net.nature.api.test;

import static com.jayway.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;

import org.junit.Before;
import org.junit.Test;

import com.jayway.restassured.RestAssured;

public class FeedbackTest {
	
	@Before
	public void setUp(){
		RestAssured.baseURI = "http://localhost";
		RestAssured.port = 5000;
		RestAssured.basePath = "/api";
	}
	
	@Test
	public void  get_single_feedback() {
		get("/feedback/1")
		.then()
			.body("data.kind", equalTo("Comment"))
		.and()
			.body("data.account.username", equalTo("tomyeh"));
	}

	@Test
	public void  get_feedbacks_by_tomyeh() {
		get("/account/tomyeh/feedbacks")
			.then()
			.body("data.kind", hasSize(5))			
			.body("data.account.username", everyItem(equalTo("tomyeh")));
	}

	@Test
	public void  get_feedbacks_about_a_note() {
		get("/note/20/feedbacks")
			.then()
			.body("data.kind", hasSize(2));
	}

	@Test
	public void  create_feedback_comment_about_a_note_by_carol() {
		given().
		 	param("content", "this is a new comment").
		when().
			post("/note/3/feedback/carol/new/comment")
		.then()
			.body("data.kind", equalTo("Comment"))
			.body("data.account.username", equalTo("carol"))
			.body("data.model", equalTo("Note"))
			.body("data.content", equalTo("this is a new comment"));
	}
	
	@Test
	public void  create_feedback_comment_about_a_media_by_carol() {
		given().
		 	param("content", "this is a new comment").
		when().
			post("/media/3/feedback/carol/new/comment")
		.then()
			.body("data.kind", equalTo("Comment"))
			.body("data.account.username", equalTo("carol"))
			.body("data.model", equalTo("Media"))
			.body("data.content", equalTo("this is a new comment"));
	}

	@Test
	public void  get_feedbacks_about_a_media() {
		get("/media/1/feedbacks")
		.then()
		.body("data.kind", hasSize(3))
		.body("data.kind", hasItems("Comment"));
	}
}