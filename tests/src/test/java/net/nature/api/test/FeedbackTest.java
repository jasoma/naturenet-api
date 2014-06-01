package net.nature.api.test;

import static com.jayway.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;

import java.util.Date;

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
			post("/feedback/new/comment/for/note/3/by/carol")
		.then()
			.body("data.kind", equalTo("comment"))
			.body("data.account.username", equalTo("carol"))
			.body("data.target.model", equalTo("Note"))
			.body("data.target.id", equalTo(3))
			.body("data.content", equalTo("this is a new comment"));
	}
	
	@Test
	public void  create_feedback_rating_about_a_media_by_carol() {
		given().
		 	param("content", "5").
		when().
			post("/feedback/new/rating/for/media/3/by/carol")
		.then()
			.body("data.kind", equalTo("rating"))
			.body("data.account.username", equalTo("carol"))
			.body("data.target.model", equalTo("Media"))
			.body("data.target.id", equalTo(3))
			.body("data.content", equalTo("5"));
	}
	
	@Test
	public void  create_feedback_like_about_a_context_by_mike() {
		given().		 	
		when().
			post("/feedback/new/like/for/context/1/by/mike")
		.then()
			.body("data.kind", equalTo("like"))
			.body("data.account.username", equalTo("mike"))
			.body("data.target.model", equalTo("Context"))
			.body("data.target.id", equalTo(1));
	}
	
	@Test
	public void  create_feedback_comment_about_a_user_by_tomyeh() {
		given().		
			param("content", "good insight from this person").
		when().
			post("/feedback/new/comment/for/account/2/by/tomyeh")
		.then()
			.body("data.kind", equalTo("comment"))
			.body("data.account.username", equalTo("tomyeh"))
			.body("data.target.model", equalTo("Account"))
			.body("data.target.id", equalTo(2))
			.body("data.content", equalTo("good insight from this person"));
	}	
	

	@Test
	public void  get_feedbacks_about_a_media() {
		get("/media/1/feedbacks")
		.then()
		.body("data.kind", hasSize(3))
		.body("data.kind", hasItems("Comment"));
	}
	
	@Test
	public void  update_feedback() {
		String string = "some new feedback" + (new Date()).toString();
		given().		
			param("content", string).
			param("username", "tomyeh").
		when().
			post("/feedback/1/update")
		.then()
			.body("data.content", equalTo(string));
	}	
}