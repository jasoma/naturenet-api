package net.nature.api.test;

import static com.eclipsesource.restfuse.Assert.assertOk;
import static org.hamcrest.Matchers.*;

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

public class MediaTest {

//	@Rule
//	public Destination destination = new Destination(this, "http://localhost:5000");
//
//	@Context
//	private Response response; // will be injected after every request

	
//	@HttpTest(method = Method.POST, 
//			path = "/api/media/new",
//			content = "{ \"title\" : \"some new media\"" +
//					", \"note_id\" : 2" +
//					", \"kind\" : \"Photo\"}  ")
	@Test
	public void  create_succeed() {
		
//		assertOk(response);
//		String json = response.getBody();		
//		System.out.println(json);
//		JsonAssert.with(json).assertThat("$media.kind", equalTo("Photo"));
//		JsonAssert.with(json).assertThat("$media.title", equalTo("some new media"));
	}
	
	
}