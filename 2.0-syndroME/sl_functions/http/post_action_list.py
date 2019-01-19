import sl_functions.http.post_actions.post_test as post_test
import sl_functions.http.post_actions.file_upload as file_upload

post_list = {
    "/post_test.post":post_test.post_test,
	"/file_upload.post":file_upload.file_upload
    }
gept_list = {
    "/post_test.post":post_test.post_test
    }
