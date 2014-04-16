package net.nature.api.test;

import static com.eclipsesource.restfuse.Assert.assertOk;
import static org.hamcrest.Matchers.*;

import org.junit.Rule;
import org.junit.runner.RunWith;

import com.eclipsesource.restfuse.Destination;
import com.eclipsesource.restfuse.HttpJUnitRunner;
import com.eclipsesource.restfuse.Method;
import com.eclipsesource.restfuse.Response;
import com.eclipsesource.restfuse.annotation.Context;
import com.eclipsesource.restfuse.annotation.HttpTest;
import com.jayway.jsonassert.JsonAssert;

@RunWith( HttpJUnitRunner.class )
public class NoteTest {

	@Rule
	public Destination destination = new Destination(this, "http://localhost:5000");

	@Context
	private Response response; // will be injected after every request

	@HttpTest( method = Method.GET, path = "/api/note/1" )
	public void  get() {
		assertOk(response);
		String json = response.getBody();		
		JsonAssert.with(json).assertThat("$note.kind", equalTo("FieldNote"));
		JsonAssert.with(json).assertThat("$note.context.name", equalTo("ask"));
	}  
	
	@HttpTest(method = Method.POST, 
			path = "/api/note/new",
			content = "{ \"username\" : \"tomyeh\"" +
					", \"content\" : \"new note\"" +
					", \"context\" : \"ask\"  " +
					", \"kind\" : \"FieldNote\"}  ")
	public void  create_succeed() {
		assertOk(response);
		String json = response.getBody();		
		System.out.println(json);
		JsonAssert.with(json).assertThat("$note.kind", equalTo("FieldNote"));
		JsonAssert.with(json).assertThat("$note.content", equalTo("new note"));
		JsonAssert.with(json).assertThat("$note.context.name", equalTo("ask"));
		JsonAssert.with(json).assertThat("$note.account.username", equalTo("tomyeh"));
	}
	
	
	@HttpTest( method = Method.POST, 
			path = "/api/note/new",
			content = "{}")
	public void  create_fails_without_data() {
		assertOk(response);
		String json = response.getBody();		
		JsonAssert.with(json).assertThat("$success", equalTo(false));
	}  
	
	@HttpTest( method = Method.POST, 
			path = "/api/note/new",
			content = "{ \"username\" : \"nobody\"} ")
	public void  create_fails_username_does_not_exist() {
		assertOk(response);
		String json = response.getBody();		
		JsonAssert.with(json).assertThat("$success", equalTo(false));
	}  	
}