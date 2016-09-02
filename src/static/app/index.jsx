//required imports for the functions
import {render} from 'react-dom';
import SearchRecipe from './SearchRecipe';
import ItemDetailsRecipe from './ItemDetailsRecipe';

//cooking function
export function cookRecipe (recipe, params, elementId) {
	if(recipe.type === 'item-details') {
		render(<ItemDetailsRecipe ingredients={recipe.ingredients} params={params}/>, document.getElementById(elementId));
	} else if(recipe.type === 'search') {
		render(<SearchRecipe ingredients={recipe.ingredients} params={params}/>, document.getElementById(elementId));
	} else {
		console.error('Please provide a valid recipe');
	}
}

//apis
export {default as AnnotationAPI} from './api/AnnotationAPI';
export {default as CollectionAPI} from './api/CollectionAPI';
export {default as SearchAPI} from './api/SearchAPI';

//collection components
export {default as CollectionSelector} from './components/collection/CollectionSelector';
export {default as CollectionStats} from './components/collection/CollectionStats';
export {default as CollectionAnalyser} from './components/collection/CollectionAnalyser';

//search components
export {default as FacetSearchComponent} from './components/search/FacetSearchComponent';
export {default as ComparativeSearch} from './components/search/ComparativeSearch';
export {default as SearchSnippet} from './components/search/SearchSnippet';
export {default as ItemDetails} from './components/search/ItemDetails';
export {default as FlexHits} from './components/search/FlexHits';

//data visualisation components
export {default as LineChart} from './components/stats/LineChart';

//flex components
export {default as FlexBox} from './components/FlexBox';
export {default as FlexModal} from './components/FlexModal';
export {default as FlexComponentInfo} from './components/FlexComponentInfo';

//annotation components
export {default as AnnotationBox} from './components/annotation/AnnotationBox';
export {default as CommentingForm} from './components/annotation/CommentingForm';
export {default as ClassifyingForm} from './components/annotation/ClassifyingForm';
export {default as LinkingForm} from './components/annotation/LinkingForm';

//video players
export {default as FlexPlayer} from './components/player/video/FlexPlayer';
export {default as VimeoPlayer} from './components/player/video/VimeoPlayer';
export {default as YouTubePlayer} from './components/player/video/YouTubePlayer';
export {default as JWPlayer} from './components/player/video/JWPlayer';

//image viewer
export {default as FlexImageViewer} from './components/player/image/FlexImageViewer';

//utils
export {default as CollectionDataUtil} from './util/CollectionDataUtil';
export {default as CollectionUtil} from './util/CollectionUtil';
export {default as TimeUtil} from './util/TimeUtil';

//collection mappings (should they be here?)
export {default as CollectionConfig} from './collection/mappings/CollectionConfig';
export {default as NISVCatalogueConfig} from './collection/mappings/NISVCatalogueConfig';
export {default as NISVProgramGuideConfig} from './collection/mappings/NISVProgramGuideConfig';
export {default as SpeechAndernieuwsConfig} from './collection/mappings/SpeechAndernieuwsConfig';