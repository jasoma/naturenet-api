package net.nature.api.test;

import static com.eclipsesource.restfuse.Assert.assertOk;
import static org.hamcrest.Matchers.*;

import java.io.File;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;

import com.eclipsesource.restfuse.Destination;
import com.eclipsesource.restfuse.HttpJUnitRunner;
import com.eclipsesource.restfuse.Method;
import com.eclipsesource.restfuse.Response;
import com.eclipsesource.restfuse.annotation.Context;
import com.eclipsesource.restfuse.annotation.HttpTest;
import com.jayway.jsonassert.JsonAssert;
import com.jayway.restassured.RestAssured;

import static com.jayway.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;


public class MediaTest {

	@Before
	public void setUp(){
		RestAssured.baseURI = "http://localhost";
		RestAssured.port = 5000;
		RestAssured.basePath = "/api";
	}

	@Test
	public void get_a_media(){
		get("/media/1")
		.then()
			.body("data.kind", equalTo("Photo"))
			.body("data.title", equalTo("photo of a bird"));
	}
	
	@Test
	public void  create_succeed() {
		
		int id =
		given().
        	multiPart(new File("test.png")).
        	parameter("title","title of image").
        when().
        	post("/note/1/new/photo").
        then().
        	body("data.title", equalTo("title of image")).
        	body("data.link", startsWith("http")).
        	body("data.link", containsString("cloudinary")).
		extract().
        	path("data.id");
		
		get("/media/{id}", id)
		.then()
			.body("data.kind", equalTo("Photo"))
			.body("data.title", equalTo("title of image"));
		
	}
	
	
}