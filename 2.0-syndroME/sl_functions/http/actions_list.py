import sl_functions.http.actions.post_test as post_test
import sl_functions.http.actions.file_upload as file_upload
import sl_functions.http.actions.get_all_images as get_all_images

post_list = {
    "/post_test.post":post_test.post_test,
    "/file_upload.post":file_upload.file_upload,
    "/get_all_images.post":get_all_images.get_all_images
    }
gept_list = {
    "/post_test.post":post_test.post_test,
    "/file_upload.post":file_upload.file_upload,
    "/get_all_images.post":get_all_images.get_all_images    
    }