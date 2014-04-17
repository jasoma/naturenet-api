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
public class FeedbackTest {

	@Rule
	public Destination destination = new Destination(this, "http://localhost:5000");

	@Context
	private Response response; // will be injected after every request

	@HttpTest( method = Method.GET, path = "/api/feedback/1" )
	public void  get() {
		assertOk(response);
		String json = response.getBody();		
		JsonAssert.with(json).assertThat("$feedback.kind", equalTo("Comment"));
		JsonAssert.with(json).assertThat("$feedback.account.username", equalTo("tomyeh"));
	}  
	
	@HttpTest( method = Method.GET, path = "/api/account/tomyeh/feedbacks" )
	public void  get_feedbacks_by_tomyeh() {
		assertOk(response);
		String json = response.getBody();
		JsonAssert.with(json).assertThat("$feedbacks..kind", hasSize(5));
	}
	
	@HttpTest( method = Method.GET, path = "/api/note/20/feedbacks" )
	public void  get_feedbacks_about_a_note() {
		assertOk(response);
		String json = response.getBody();
		JsonAssert.with(json).assertThat("$feedbacks..kind", hasSize(2));
	}
	
	@HttpTest( method = Method.POST,
			path = "/api/note/3/feedback/carol/new/comment",
			content = "{ \"content\" : \"this is a new comment\"}")
	public void  create_feedback_comment_about_a_note_by_carol() {
		assertOk(response);
		String json = response.getBody();
		JsonAssert.with(json).assertThat("$feedback.kind", equalTo("Comment"));
		JsonAssert.with(json).assertThat("$feedback.content", equalTo("this is a new comment"));
		JsonAssert.with(json).assertThat("$feedback.model", equalTo("Note"));
		JsonAssert.with(json).assertThat("$feedback.account.username", equalTo("carol"));
	}
	
	@HttpTest( method = Method.POST,
			path = "/api/media/3/feedback/carol/new/comment",
			content = "{ \"content\" : \"this is a new comment\"}")
	public void  create_feedback_comment_about_a_media_by_carol() {
		assertOk(response);
		String json = response.getBody();
		JsonAssert.with(json).assertThat("$feedback.kind", equalTo("Comment"));
		JsonAssert.with(json).assertThat("$feedback.model", equalTo("Media"));
		JsonAssert.with(json).assertThat("$feedback.content", equalTo("this is a new comment"));
		JsonAssert.with(json).assertThat("$feedback.account.username", equalTo("carol"));
	}
	

	@HttpTest( method = Method.GET, path = "/api/media/1/feedbacks" )
	public void  get_feedbacks_about_a_media() {
		assertOk(response);
		String json = response.getBody();
		JsonAssert.with(json).assertThat("$feedbacks..kind", hasSize(3));
		JsonAssert.with(json).assertThat("$feedbacks..kind", hasItems("Comment"));
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