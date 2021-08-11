import { StyleSheet, Dimensions } from 'react-native';
import {
    DEFAULT_TEXT_COLOR, FONT,
    LOADING_BACKGROUND, POPUP_BACKGROUND,
    TEXT_INPUT_BORDER, TEXT_INPUT_BACKGROUND,
    BORDER_COLOR, TITLE_UNDERLAY_COLOR, DIALOG_TEXT_COLOR
} from './Colors.js'

var {height, width} = Dimensions.get('window')

export const isiPhoneX = (height == 812 && width == 375);
export const isiPhone5 = (height == 568 && width == 320);
export const isiPhone = (height == 667 && width == 375);
export const isiPhonePlus = (height == 736 && width == 414);

export const styles = StyleSheet.create({
    fullscreen: {
        top: '0%',
        width:'100%',
        height:'93%'
    },
    tabContent: {
        height:'100%'
    },
    fullWidthButtonText: {
        fontFamily: FONT,
        justifyContent: 'center',
        alignItems: 'center'
    },
    loginFullscreen:{
        flex:1,
        top: '0%',
        width:'100%',
        height:'100%',
        alignItems: 'center',
    },
    buttonCenter: {
        top:'70%',
        width:'80%'
    },
    backgroundVideo: {
        position: 'absolute',
        top: 0,
        left: 0,
        bottom: 0,
        right: 0,
    },
    titleText: {
        backgroundColor:'transparent', 
        fontFamily:'System',
        top:0.33 * height - 21,
        fontSize: 36,
        fontWeight: 'bold' 
    },
    container: {
        flex:1,
        backgroundColor: 'white',
    },
    list: {
        top:'2%',
        justifyContent: 'center',
        alignItems: 'center',
        flexDirection: 'row',
        flexWrap: 'wrap'
    },
    item: {
        alignItems: 'center',
        width:100, 
        height:100,
        marginBottom:30,
        marginLeft: 10,
        marginRight : 10
    },
    text: {
        fontFamily: FONT,
        textAlign: 'center', 
        top: '40%',
        color: DEFAULT_TEXT_COLOR,
        fontSize:16
    },
    center: {
        alignItems:'center', 
        justifyContent:'center'
    },
    sliderContainer:{
        width:'100%'
    },
    slider: {
        marginLeft: 10,
        marginRight: 10,
        alignItems: "stretch",
        justifyContent: "center"
    },
    loading: {
        position: 'absolute',
        left: 0,
        right: 0,
        top: 0,
        bottom: 0,
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: LOADING_BACKGROUND
    },
    popupBase: {
        flexDirection: 'column', 
        backgroundColor:POPUP_BACKGROUND
    },
    popupTwoButtons: {
        top:'0%', 
        flexDirection:'row', 
        alignItems:'center', 
        justifyContent:'center'
    },
    headerRightIcon: {
        right: 10
    },
    headerLeftIcon: {
        left: 10
    },
    settingAvatar: {
        top:"0%", 
        marginBottom:"5%", 
        alignItems: 'center'
    },
    sliderTitle: {
        flex: 1, 
        flexDirection: 'row', 
        justifyContent:'space-between'
    },
    textFont: {
        fontFamily:FONT
    },
    discoverMenuButton: {
        left: 7,
        fontFamily: FONT
    },
    chatMenuButton: {
        left: 10,
        fontFamily: FONT
    },
    border: {
        borderColor: TEXT_INPUT_BORDER, 
        borderWidth: 2, 
        borderRadius: 8
    },
    textInput: {
        width:"90%", 
        borderColor: TEXT_INPUT_BORDER, 
        borderWidth: 2, 
        fontSize:16, 
        height:24, 
        backgroundColor:TEXT_INPUT_BACKGROUND, 
        borderRadius:20, 
        paddingLeft:8, 
        paddingRight:8
    },
    avatarPopup: {
        bottom:"20%", 
        flexDirection: 'column',
        backgroundColor:'transparent'
    },
    avatarStyle: {
        flex:1, 
        justifyContent: 'center', 
        alignItems:'center'
    },
    requestItem: {
        marginRight:40, 
        marginTop:10
    },
    requestTitle: {
        fontFamily: FONT, 
        fontWeight:'bold', 
        top:'2%', 
        left:'3%', 
        color:DEFAULT_TEXT_COLOR, 
        fontSize:16
    },
    requestText: {
        top:'0%', 
        height:'11.5%'
    },
    requestMessage: {
        top:'3%', 
        flexDirection: 'column', 
        justifyContent: 'center', 
        alignItems:'center'
    },
    requestMessageStyle: {
        width:"90%",
        alignItems:'center'
    },
    flexRow: {
        flexDirection:'row'
    },
    flexCol: {
        flexDirection: 'column'
    },
    flexOne: {
        flex:1
    },
    dialogTitleView: {
        borderTopLeftRadius: 8,
        borderTopRightRadius: 8,
        padding: 14,
        borderBottomWidth: 0.5,
        backgroundColor: TITLE_UNDERLAY_COLOR,
        borderColor: BORDER_COLOR,
        alignItems: 'center'
    },
    dialogTitleText: {
        color: DIALOG_TEXT_COLOR,
        fontSize: 16,
    },
    borderRadiusPopup:{
        borderRadius: 20
    },
    chatTags: {
        height:30, 
        fontSize:18, 
        width:"90%", 
        margin:10,
        fontWeight: 'bold',
        color:'white'
    },
    tags: {
        height:25, 
        fontSize:16,
        marginLeft:10, 
        marginRight:10,
    }
});
