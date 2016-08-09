import PlayerAPI from './PlayerAPI';
//See https://developers.google.com/youtube/iframe_api_reference

class YouTubePlayer extends React.Component {

	constructor(props) {
		super(props);
		this.state = {
			player : null
		}
	}

	componentDidMount() {
		if(!document.getElementById('youtubeiframeapi')) {
			console.debug('Loading the iframe API');
			var tag = document.createElement('script');
			tag.id = 'youtubeiframeapi';
			tag.src = "https://www.youtube.com/iframe_api";
			var firstScriptTag = document.getElementsByTagName('script')[0];
			firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
			window.onYouTubeIframeAPIReady = this.onYouTubeIframeAPIReady.bind(this);
		} else {
			this.onYouTubeIframeAPIReady();
		}
	}

	componentDidUpdate() {
		if(!this.state.player) {
			this.onYouTubeIframeAPIReady();
		}
	}

	componentWillUnmount() {
		console.debug('Destroying the YouTube player');
		if(this.state.player) {
			this.state.player.destroy();
		}
	}

	onYouTubeIframeAPIReady() {
		console.debug('Got a player');
		let player = new YT.Player('video_player', {
			height: '390',
			width: '640',
			videoId: this.getVideoId(),//M7lc1UVf-VE
			events: {
				'onReady': this.onPlayerReady.bind(this),
				'onStateChange': this.onPlayerStateChange.bind(this)
			}
		});
		this.setState({player: player});
	}

	getVideoId() {
		if(!this.props.mediaObject) return null;
		return this.props.mediaObject.url.substring(this.props.mediaObject.url.indexOf('v=') + 2);

	}

	onPlayerReady(event) {
		if(this.props.onPlayerReady) {
			//send back the api to the owning component
			this.props.onPlayerReady(new YouTubeAPI(this.state.player));
		}

		//the youtube iframe API does not have an equivalent of onTime or onProgress.
		this.videotime = 0;
  		setInterval(this.updateTime.bind(this), 100);
	}

	updateTime() {
		var oldTime = this.videotime;
		if(this.state.player && this.state.player.getCurrentTime) {
			this.videotime = this.state.player.getCurrentTime();
		}
		if(this.videotime !== oldTime) {
			this.onProgress(this.videotime);
		}
	}

	onProgress(currentTime) {
		this.props.eventCallbacks.playProgress(currentTime);
	}

	onPlayerStateChange(event) {
		switch (event.data) {
			case YT.PlayerState.BUFFERING : this.props.eventCallbacks.loadProgress(event);break;
			case YT.PlayerState.PLAYING : this.props.eventCallbacks.onPlay(event);break;
			case YT.PlayerState.PAUSED : this.props.eventCallbacks.onPause(event);break;
			case YT.PlayerState.ENDED : this.props.eventCallbacks.onFinish(event);break;
		}
	}

	render() {
		return (
			<div id="video_player"/>
		)
	}
}

class YouTubeAPI extends PlayerAPI {

	constructor(playerAPI) {
		super(playerAPI);
	}

	/* ------------ Implemented API calls ------------- */

	play() {
		this.playerAPI.playVideo();
	}

	pause() {
		this.playerAPI.pauseVideo();
	}

	seek(secs) {
		this.playerAPI.seekTo(secs);
	}

	getPosition(callback) {
		callback(this.playerAPI.getCurrentTime());
	}

	getDuration(callback) {
		callback(this.playerAPI.getDuration());
	}

	isPaused(callback) {
		callback(this.playerAPI.getPlayerState() == 2);
	}

}

export default YouTubePlayer;