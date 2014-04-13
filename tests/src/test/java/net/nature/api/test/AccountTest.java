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
public class AccountTest {

	@Rule
	public Destination destination = new Destination(this, "http://localhost:5000");

	@Context
	private Response response; // will be injected after every request

	@HttpTest( method = Method.GET, path = "/api" )
	public void checkAPIOnlineStatus() {
		assertOk( response );
	}  

	@HttpTest( method = Method.GET, path = "/api/accounts/count" )
	public void  accountCount() {
		String json = response.getBody();
		JsonAssert.with(json).assertThat("$data", greaterThan(1));
	}  

	@HttpTest( method = Method.GET, path = "/api/account/tomyeh" )
	public void  accountGet_tomyeh() {
		String json = response.getBody();
		JsonAssert.with(json).assertThat("$username", equalTo("tomyeh"));
	}
	
	@HttpTest( method = Method.GET, path = "/api/account/abby" )
	public void  accountGet_abby() {
		String json = response.getBody();
		JsonAssert.with(json).assertThat("$username", equalTo("abby"));
	}  

	@HttpTest( method = Method.GET, path = "/api/accounts" )
	public void  accountGetAllUserNames() {
		String json = response.getBody();
		JsonAssert.with(json).assertThat("$..username", hasItems("tomyeh","abby"));
	}  
	
	@HttpTest( method = Method.GET, path = "/api/account/tomyeh/notes" )
	public void  accountGetNotes_tomyeh() {
		String json = response.getBody();
		JsonAssert.with(json).assertThat("$..content", hasItems("first note taken by tomyeh"));
		JsonAssert.with(json).assertThat("$..medias.title", hasItems("photo of a bird", "video of a bird"));
		JsonAssert.with(json).assertThat("$..medias.kind", hasItems("Photo","Video"));
	}  
	
	@HttpTest( method = Method.GET, path = "/api/account/abby/notes" )
	public void  accountGetNotes_abby() {
		String json = response.getBody();
		JsonAssert.with(json).assertThat("$..content", hasItems("first note taken by abby"));
		JsonAssert.with(json).assertThat("$..medias.title", hasItems("photo of a bird"));
		JsonAssert.with(json).assertThat("$..medias.kind", hasItems("Photo"));
	}  
	
	
}