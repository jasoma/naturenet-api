package net.nature.api.test;

import static org.hamcrest.Matchers.greaterThan;

import java.io.File;

import org.junit.Before;
import org.junit.Test;

import retrofit.RestAdapter;
import retrofit.client.Response;
import retrofit.http.GET;
import retrofit.http.Multipart;
import retrofit.http.POST;
import retrofit.http.PUT;
import retrofit.http.Part;
import retrofit.mime.TypedFile;
import retrofit.mime.TypedString;


import com.eclipsesource.restfuse.Method;
import com.eclipsesource.restfuse.annotation.HttpTest;
import com.jayway.jsonassert.JsonAssert;
import com.jayway.restassured.RestAssured;

import static com.jayway.restassured.RestAssured.*;
import static com.jayway.restassured.matcher.RestAssuredMatchers.*;
import static org.hamcrest.Matchers.*;

interface NatureNetService {
	@GET("/api")
	Response api();
	
//	@POST("/upload")
//	Response upload();
	
	@Multipart
	@POST("/upload")
	Response upload(@Part("photo") TypedFile photo);//, @Part("description") TypedString description);
}

public class MediaUploadTest {
	
	private NatureNetService service;

	@Before
	public void setUp(){
		RestAdapter restAdapter = new RestAdapter.Builder()
		.setEndpoint("http://localhost:5000")
		.build();

		service = restAdapter.create(NatureNetService.class);
		
		
		
		RestAssured.baseURI = "http://localhost";
		RestAssured.port = 5000;
		RestAssured.basePath = "/api";
	}
	
	
	@Test
	public void  count() {
		get("/accounts/count").then().body("data", greaterThan(5));
	}  
	

	@Test
	public void test(){
		Response response = service.upload(new TypedFile("image/png",new File("test.png")));
		System.out.println(response.toString());
	}
}
