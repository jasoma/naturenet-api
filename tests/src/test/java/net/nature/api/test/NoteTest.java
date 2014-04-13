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
	public void  noteGet() {
		assertOk(response);
		String json = response.getBody();		
		JsonAssert.with(json).assertThat("$.kind", equalTo("FieldNote"));
		JsonAssert.with(json).assertThat("$.context.name", equalTo("ask"));
	}  
	
}