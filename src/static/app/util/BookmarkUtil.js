import AnnotationAPI from '../api/AnnotationAPI';

const BookmarkUtil = {

	bookmark : function(user, project, bookmarkType, data, callback) {
		console.debug('Bookmarking for: ' + user);
		AnnotationAPI.saveAnnotation(
			BookmarkUtil.generateAnnotation(user, project, bookmarkType, data),
			callback
		);
	},

	hasBookmarkSupport : function(bookmarkType, annotationConfig) {
		if(annotationConfig && annotationConfig[bookmarkType] && annotationConfig[bookmarkType].modes) {
			return annotationConfig[bookmarkType].modes.indexOf('bookmark') != -1;
		}
		return false;
	},

	//the target of a bookmark is a project of a certain user, which should be dereferencable in the user space
	generateAnnotation : function(user, project, bookmarkType, data) {
		project = project ? project : 'default'; //revert to the default project if the project is not provided
		return {
			//the data attribute is the only thing that is not w3c compliant and is interpreted on the server
			data:
				{
					bookmarks: [{
						type : 'query',
						data : data
					}],
				}
			,
			//these properties are directly copied into the w3c annotation on the server
			motivation: 'bookmarking',
			target: {
				source: 'http://' + user + '.clariah.nl/' + project
			}
		}
	}

}

export default BookmarkUtil;