import React from 'react';

class ItemDetails extends React.Component {

	constructor(props) {
		super(props);
	}

	render() {

		//draw the unique metadata
		let uniqueMetadata = Object.keys(this.props.data).map((key, index)=> {
			if(typeof this.props.data[key] == 'string' && key[0] != '_') {
				return (
					<tr key={'props__' + index}>
						<td><strong>{key}:</strong></td>
						<td>{this.props.data[key]}</td>
					</tr>
				);
			}
		});

		let metadata = (
			<table className="table">
				<tbody>
					<tr>
						<td><strong>id:</strong></td>
						<td>{this.props.data._id}</td>
					</tr>
					<tr>
						<td><strong>index:</strong></td>
						<td>{this.props.data._index}</td>
					</tr>
					<tr>
						<td><strong>document type:</strong></td>
						<td>{this.props.data._type}</td>
					</tr>
					{uniqueMetadata}
				</tbody>
			</table>
		)

		//draw the block with different media objects
		let mediaBlock = '';
		if(this.props.data['playableContent']) {
			//TODO cluster all of the media players, so it's possible to draw them in a separate panel for each media type
			let mediaItems = this.props.data['playableContent'].map((mediaItem, index) => {
				let mediaPlayer = 'Unknown Media Object: ' + index;

				/*
				* Draw a media player based on the mimetype of each item
				* TODO put each player in a separate React component
				*/
				if(mediaItem.mimeType.indexOf('image') != -1) {//image player
					mediaPlayer = (
						<a href={mediaItem.url}
							target="__external">
							<img src={mediaItem.url}/>
						</a>
					)
				} else if(mediaItem.mimeType.indexOf('audio') != null) {//audio player
					mediaPlayer = (
						<audio controls>
							<source src={mediaItem.url} type={mediaItem.mimeType}/>
							Your browser does not support the audio element
						</audio>
					)
				} else if(mediaItem.mimeType.indexOf('video') != -1) {//video player
					mediaPlayer = (
						<video width="320" height="240" controls>
							<source src={mediaItem.url} type={mediaItem.mimeType}/>
							Your browser does not support the video element
						</video>
					)
					//deze zou video moeten hebben:
					//https://easy.dans.knaw.nl/oai/?verb=GetRecord&identifier=oai:easy.dans.knaw.nl:easy-dataset:60508&uniqueMetadataPrefix=oai_dc
					//in ES: nederlandse-oud-gevangenen-van-kamp-buchenwald
				}

				return (
					<div key={'media__' + index} className="media-player">
						{mediaPlayer}
					</div>
				);
			});

			//only show the first 5 media items for now
			mediaBlock = (
				<div className="panel panel-default">
					<div className="panel-heading">Media</div>
					<div className="panel-body">
						{mediaItems.slice(0, 5)}
					</div>
				</div>
			);

			}
		return (
			<div>
				<div className="panel panel-default">
					<div className="panel-heading">Metadata</div>
					<div className="panel-body">
						{metadata}
					</div>
				</div>
				{mediaBlock}
			</div>
		)
	}
}

export default ItemDetails;