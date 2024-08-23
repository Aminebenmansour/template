require "test_helper"

class ForumsControllerTest < ActionDispatch::IntegrationTest
  test "should get index" do
    get forums_index_url
    assert_response :success
  end
end
