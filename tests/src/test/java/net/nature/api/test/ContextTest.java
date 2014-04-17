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
public class ContextTest {

	@Rule
	public Destination destination = new Destination(this, "http://localhost:5000");

	@Context
	private Response response; // will be injected after every request

	@HttpTest(method = Method.GET, 
			path = "/api/context/1")
	public void  get() {
		assertOk(response);
		String json = response.getBody();		
		JsonAssert.with(json).assertThat("$context.kind", equalTo("Activity"));
		JsonAssert.with(json).assertThat("$context.name", equalTo("ask"));
	}
	
	@HttpTest(method = Method.GET, 
			path = "/api/context/1/notes")
	public void  get_notes() {
		assertOk(response);		
		String json = response.getBody();
		JsonAssert.with(json).assertThat("$notes..context.id", everyItem(equalTo(1)));
	}
	
	@HttpTest(method = Method.GET, 
			path = "/api/context/activities")
	public void  get_all_activities() {
		assertOk(response);
		String json = response.getBody();		
		JsonAssert.with(json).assertThat("$..kind", everyItem(equalTo("Activity")));
	}
	
	@HttpTest(method = Method.GET, 
			path = "/api/context/landmarks")
	public void  get_all_landmarks() {
		assertOk(response);
		String json = response.getBody();		
		JsonAssert.with(json).assertThat("$..kind", everyItem(equalTo("Landmark")));
	}
	
	
}