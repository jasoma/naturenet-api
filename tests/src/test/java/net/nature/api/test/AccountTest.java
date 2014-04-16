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
	public void  count() {
		String json = response.getBody();
		JsonAssert.with(json).assertThat("$data", greaterThan(1));
	}  

	@HttpTest( method = Method.GET, path = "/api/account/tomyeh" )
	public void  get_tomyeh() {
		String json = response.getBody();
		JsonAssert.with(json).assertThat("$account.username", equalTo("tomyeh"));
	}
	
	@HttpTest( method = Method.POST, 
			path = "/api/account/new", 
			content = "{ \"username\" : \"newbie\"} ")
	public void  create_new() {
		String json = response.getBody();
		JsonAssert.with(json).assertThat("$account.username", equalTo("newbie"));
	}
	
	@HttpTest( method = Method.POST, 
			path = "/api/account/new", 
			content = "{ \"username\" : \"tomyeh\"} ")
	public void  create_new_but_username_already_exists() {
		String json = response.getBody();
		JsonAssert.with(json).assertThat("$success", equalTo(false));
	}	
	
	
	@HttpTest( method = Method.GET, path = "/api/account/abby" )
	public void  get_abby() {
		String json = response.getBody();
		JsonAssert.with(json).assertThat("$account.username", equalTo("abby"));
	}  

	@HttpTest( method = Method.GET, path = "/api/accounts" )
	public void  get_all_accounts() {
		String json = response.getBody();
		JsonAssert.with(json).assertThat("$accounts..username", hasItems("tomyeh","abby"));
	}  
	
	@HttpTest( method = Method.GET, path = "/api/account/tomyeh/notes" )
	public void  get_notes_for_tomyeh() {
		String json = response.getBody();
		JsonAssert.with(json).assertThat("$notes..content", hasItems("first note taken by tomyeh"));
		JsonAssert.with(json).assertThat("$notes..medias.title", hasItems("photo of a bird", "video of a bird"));
		JsonAssert.with(json).assertThat("$notes..medias.kind", hasItems("Photo","Video"));
	}  
	
	@HttpTest( method = Method.GET, path = "/api/account/abby/notes" )
	public void  get_notes_for_abby() {
		String json = response.getBody();
		JsonAssert.with(json).assertThat("$notes..content", hasItems("first note taken by abby"));
		JsonAssert.with(json).assertThat("$notes..medias.title", hasItems("photo of a bird"));
		JsonAssert.with(json).assertThat("$notes..medias.kind", hasItems("Photo"));
	}  
	
	
}