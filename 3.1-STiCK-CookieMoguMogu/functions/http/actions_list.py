import functions.http.actions.post_test as post_test
import functions.http.actions.file_upload as file_upload
import functions.http.actions.get_all_images as get_all_images
import functions.http.actions.cookie_test as cookie_test

post_list = {
    "/post_test.post":post_test.post_test,
    "/file_upload.post":file_upload.file_upload,
    "/get_all_images.post":get_all_images.get_all_images,
    "/cookie_test.post":cookie_test.cookie_test
    }
gept_list = {
    "/post_test.post":post_test.post_test,
    "/cookie_test.post":cookie_test.cookie_test
    }