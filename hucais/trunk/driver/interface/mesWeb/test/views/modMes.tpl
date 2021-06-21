<HTML xmlns="http://www.w3.org/1999/xhtml"><HEAD id=ctl01_ctl00><META content="IE=7.0000" http-equiv="X-UA-Compatible">
<TITLE>SIMATIC IT 门户网站</TITLE>
<META id=ctl01_ctl01 content=IE=EmulateIE7 http-equiv=X-UA-Compatible><LINK rel=stylesheet type=text/css href="../../App_Themes/MechatronicsTheme-Silver/Menu.Silver.css"><LINK rel=stylesheet type=text/css href="../../App_Themes/MechatronicsTheme-Silver/MechatronicsLibrary.css"><LINK rel=stylesheet type=text/css href="../../App_Themes/MechatronicsTheme-Silver/Menu.Outlook.css"><LINK rel=stylesheet type=text/css href="../../App_Themes/MechatronicsTheme-Silver/Menu.Silver.css"><LINK rel=stylesheet type=text/css href="../../App_Themes/MechatronicsTheme-Silver/StyleSheet.css"><LINK rel=stylesheet type=text/css href="../../App_Themes/MechatronicsTheme-Silver/Default/ig_dataGrid.css"><LINK rel=stylesheet type=text/css href="../../App_Themes/MechatronicsTheme-Silver/Default/ig_datamenu.css"><LINK rel=stylesheet type=text/css href="../../App_Themes/MechatronicsTheme-Silver/Default/ig_datatree.css"><LINK rel=stylesheet type=text/css href="../../App_Themes/MechatronicsTheme-Silver/Default/ig_dropDown.css"><LINK rel=stylesheet type=text/css href="../../App_Themes/MechatronicsTheme-Silver/Default/ig_explorerbar.css"><LINK rel=stylesheet type=text/css href="../../App_Themes/MechatronicsTheme-Silver/Default/ig_shared.css"><LINK rel=stylesheet type=text/css href="../../App_Themes/MechatronicsTheme-Silver/Default/ig_menu.css"><LINK rel=stylesheet type=text/css href="../../App_Themes/MechatronicsTheme-Silver/Default/ig_webtab.css"><LINK rel=stylesheet type=text/css href="../../App_Themes/MechatronicsTheme-Silver/Electronics.css">
<META name=description content="SIMATIC IT 门户网站">
<META name=keywords content="SIMATIC IT, ASP.NET 2.0, MES"><LINK rel=stylesheet type=text/css href="/SITApps/SITPortal/WebResource.axd?d=Crftir25e1BsLVrJwqJ5721ZGUmJbnc5VzbPJxyuGjt2vDhFIZiwgflMW5ieuTEeXhjLVy5GBbOuf5oGLBGkHPx2OF85ClOp2lM6CVwcJ1gJXfnY6m4MQNd3t628c3uSK0I00134Z5x2yhh6qeLqD5J5rSZXRhAwjQyspVnHzDlJ6ibf0&amp;t=634837316893750328">
<STYLE type=text/css>.ig_a0da865d_r0 {
	BORDER-TOP-STYLE: none; FONT-SIZE: 12px; WIDTH: 100%; BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; BORDER-LEFT-STYLE: none
}
.ig_a0da865d_r2 {
	CURSOR: default; COLOR: black
}
.ig_a0da865d_r8 {
	BACKGROUND-REPEAT: repeat-x
}
.ig_443c2ebe_r0 {
	WIDTH: 100%
}
.ig_a0da865d_r9 {
	CURSOR: default; COLOR: black
}
.ig_a0da865d_r11 {
	BACKGROUND-COLOR: red
}
.ig_a0da865d_r12 {
	COLOR: gray
}
</STYLE>
</HEAD>
<BODY id=Body>
<OBJECT id=SITCABTool codeBase="http://192.168.32.166/CABINET/SITCABTools.cab" classid=CLSID:FA7AC8C3-9080-4CA3-B5DA-3800FFF534EF><PARAM NAME="_Version" VALUE="65537"><PARAM NAME="_ExtentX" VALUE="0"><PARAM NAME="_ExtentY" VALUE="0"><PARAM NAME="_StockProps" VALUE="0"></OBJECT>
<FORM id=aspnetForm method=post name=aspnetForm action=modMes>
<DIV>   <INPUT id=ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_ClientState type=hidden value='{"ActiveTabIndex":0,"TabState":[true]}' name=ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_ClientState>  </DIV>
<SCRIPT type=text/javascript>
//<![CDATA[
var theForm = document.forms['aspnetForm'];
if (!theForm) {
    theForm = document.aspnetForm;
}
function __doPostBack(eventTarget, eventArgument) {
    if (!theForm.onsubmit || (theForm.onsubmit() != false)) {
        theForm.__EVENTTARGET.value = eventTarget;
        theForm.__EVENTARGUMENT.value = eventArgument;
        theForm.submit();
    }
}
//]]>
</SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/WebResource.axd?d=njHjiWe6VURyw9smwqBrYXU8kIs-Igwj7WOK0l2laPUxuwY_5k-zM47CNmrSG3bvL1Y4aNuknvTgulzyH2qRfXZaGVE1&amp;t=635588903086469712"></SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/Scripts/CabSplitterBar.js"></SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/Scripts/jquery-1.6.1.min.js"></SCRIPT>

<SCRIPT type=text/javascript>
//<![CDATA[
function doRedirLogin(){ if (typeof (WakeUp) == 'undefined') window.location.href ='/SITApps/SITPortal/PortalPage/MemberLogin.aspx?SessionExpired=true' ; }var myTimeReminder2; 
                clearTimeout(myTimeReminder2);
                myTimeReminder2 =setTimeout('doRedirLogin()',36000000);
                var myTimeReminder, myTimeOut; 
                clearTimeout(myTimeReminder); 
                clearTimeout(myTimeOut); var sessionTimeReminder = 35820000; function doReminder(){ alert('警告: 如果在接下来的 3 分钟内不执行任何操作，则将重定向到登录页面。'); }
                myTimeReminder=setTimeout('doReminder()', sessionTimeReminder);function DeleteRow(name, id, rowNum, prompt, confDelMsg)
					{
						if(confDelMsg.indexOf('{0}') != -1)
							confDelMsg = confDelMsg.replace ('{0}', name);

						event.cancelBubble = (prompt == null || prompt == true) ? confirm(confDelMsg) : true;
						if (event.cancelBubble)
							__doPostBack(id, 'Delete$' + rowNum);
						return event.cancelBubble;
					}

					function SelectRow(grid, id, rowNum)
					{
						var currentSelect = grid.attributes['selectedRow'];
						if (currentSelect == null || currentSelect.value != rowNum)
							__doPostBack(id, 'Select$' + rowNum);
					}//]]>
</SCRIPT>

<SCRIPT type=text/javascript>
//<![CDATA[
var ig_pi_imageUrl='/SITApps/SITPortal/WebResource.axd?d=ErsR1maog7xhQ_O5qI4QOzD5h2v01k1S-vY4GU26VwxcljZFywYhBD6KuFVuDQ_y0OUcX_MAYRxplh23YCGGtXx4NKdbFzbm7sTyHTf3kWpz8SupOmspQp7-TmhizltnOwOzhAEk5fzkjTzqBQu0E8RuGkDhh_plWfBkS5WgbsMHNGN5DrmkqkDT2Aa2uinT-0JA00hcY3spvgIwGVGbeM9lD5H-1sXJ-ZJ6LopgWtL2Rxff0&t=634835820579875519';try{(new Image()).src=ig_pi_imageUrl;}catch(ex){}
//]]>
</SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/ScriptResource.axd?d=dWQHnArzGPF_yx_oTWLgfPyjGVgyQtVIhwH5cUvhnvMBK0jv5SAVbwQq6cbCmXh2tTJFXi_y7XN37LnWNmzn17EjEvmKyYPkYxMRazjeMpJUtaukhPOhieIxpoF5_Bod-Z_3Jhc8QG-f2catx81p9jHo_AdmhLx8bhRRVGtD_Fi9oQYLSo7WILh-7IU4WveMYXYuPn1WPm0wfh9Lid09QcRa_1Q1&amp;t=ffffffffb096bcca"></SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/ScriptResource.axd?d=Q1t6etKJkSUxq_EwnZzzq6bLYT5ZK7wPNnrMeTAPfjZR4BUYlOYggB6UCUntIiUN2-eI14pE8z5unbH7VY-zuP-gdRlFLe30DdxrAQf-EuoYBoqGcuVTPdJsjreqPJava_uOR8ErKNBAcBdjLXuhO9uAT4ZIVrGcciu9vP6CjPqOkk0EG28nrn5Vp_UU359-UoiNH5iefrjWS_A6Y1b63fQp_IZx9EawB7uIbA1emVs5rM5x0&amp;t=ffffffffb19f2a8a"></SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/ScriptResource.axd?d=Rtle0yxxLcqU97Q-5A88r__QCZenhWRtqfj5VQSMimvvIjB2YRzmKQr96DXj1KFt9gg6GH2uHt3pDSgoHPDb7gzHJTR9aq9dFHyhCwnV93tO0Grx3LnJIhfCyS8bhQ68IEAlP1UvIqDdwNdMwtfKpR_B-wkcbEun5O3qT75j96pEOUtk0&amp;t=16d02c1c"></SCRIPT>

<SCRIPT type=text/javascript>
//<![CDATA[
Sys.Services._ProfileService.DefaultWebServicePath = '../../Profile_JSON_AppService.axd';
//]]>
</SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/ScriptResource.axd?d=wpVOyVhAOvkV2jNUr8ZQGhzz5HL-RAnqmJoQ7HDvFwOSyW4xQJvO2aqvzMgNvwDTxC5vIZ-CIsqpDb4pt7lGi8jO9hEOt2-TWaJpAgKwjYk0q4VwA7A-p-z_cMzmn2n_4QY_mU0hKcPEyQtScsTQVxOekiWch4xVLGBpMyjXYNP9s2Wt0&amp;t=16d02c1c"></SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/ScriptResource.axd?d=7T9qD9mMBLMpfpYeWwa0RZdKRSsC7I7nzz278md58j8fpv8ehzsnj1GCjPDL2SUtbKLVKCugyv28616Gwg4f5LWM_t2THo_3T17-56d4Fq7C_vJVWMdLMcCfZHMJ_QxQXnaKejplv2oWTbN6-NDhJbPvFgyGSXwZ2MMMvutpgWfOBLRYMTr_H5WTm1pP0Q816n4ftg2&amp;t=1350e4b0"></SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/ScriptResource.axd?d=CasY_-D5j7UPq8VX2_t_2NAZFzF-G3O9h71CHjIt70o8siOzMEqnr6vOCMA5Wxs16ljqtcqelknTZ7-W3Hr8CW3mJa7VY2bv_gSea4n6UnXYFq4evwm-o8kGTA8RRildPFzD5RJ4_tuTivnW-5fddd-3g_GUdLek55KEzEHA5dFQR-f2w-Ee_OYbXXj-VFLN2WOPZ6EL2q_rOTBGDmM9IOXDF_g1&amp;t=1350e4b0"></SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/ScriptResource.axd?d=sPYdN3-j2fl_N5jIZizr4QMuW4njR9HaIEDM1fgFFVIWDwAa7Vt_qJd-H9mD66CRLQ9L-BHGFWw1zTDBcWf8GAHAfafDekSJi4hJZSwzydnJEZfjYiB1MDwhDigk94lqhQwn0SninyRV2HnErRDs0PXN7mmDhCzuuSeHdU2Gd_pjY8Oy0&amp;t=1350e4b0"></SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/ScriptResource.axd?d=D7sPRdlbMc1WkVJUiACtLDdG9CY0ybjQYD2OGLjtUPdNnCpqEd2kMeP478pS4ZwNZPHXpB0kEN9H_0WdxEtlPtw-fS7nhfoqUlxOxZjjqB11ETERYwKbHZO56Gq3zbrliQaoY9pF91ynihc_GRN9uF3xdALs8Hjy_rSbCRG0ocX0F24XzbzePVfEhzY58VQUVhMaVznijkTjFj4HMYgeDUTvZ6CDRdL2FVgxNZfIOdPeiEGnm2CvnCBCpy_Q-8kWWgB3G0llXoCFIsW8-SwXx_2ejP41&amp;t=781c5f66"></SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/ScriptResource.axd?d=E9SnzrfZSBm0rNtYMjmhT7hUwl_nxhmv7Zr_lpSKU9PF1zVOR0DFBDDuyjeHCYly3dCTbZUoWKCJxLiWhD6k5Yh7avmo-DW8qDDjXOusPrrsk4qO6HFjixD-N5Rxch5chuImzxy-PxjT7k6AGbTQ4RYaOFzp-Td_iFgwRd_lAPmFE1Wqn97obdM2Wl4-waiL_GOwOASoqLfgiW3PogBfwWb3U7Q1&amp;t=1350e4b0"></SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/ScriptResource.axd?d=ii0MXijKEGoxWz6CntpdihAP5T-fZg5uy_TnTs_CpACFHtEWEaCeALu-NrBGTPdHvalSIG6zdbfQDZiIPDgSmK9wp9lC5McdjzcTjJaBLvd2yoWA20zo4cn5f7zW_zOUZLQuo797avuXGFiUgN90qFa87eTThFX9ANscXZ5IBn49gJMk1R9Jw-XYsnjHJmO8E_yygg2&amp;t=1350e4b0"></SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/ScriptResource.axd?d=mHKzurT6HrYqDcJjw2DbcycfOL-3vK1-zYYSDqwD2z59SWoQcQLqMjE-x7D3jua5jT-WU2makFNz5reYK528SZv7Twg3Y3zeDwQXAPj_mz3d-lLrzCxJ2jrTqBz0sMFNhZ4iDS7XR8wcJDZPH3b1xaaHsfI1TRcbToParGvNfwXLtRvvU7-T343htZMvgavdeGFPsA2&amp;t=1350e4b0"></SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/ScriptResource.axd?d=ncunfxkC7uCK6mFl7JWDesoVSiXGZWonIdUUY6F4muVQaQcspM5GB-uxew18Z95XRXmTef87aV-lEn43L8cCKXAbhgmxGOLIHjLqDoLe9s9Vrkub5jh7vEHeG2yap7a6IkYXahElSnpZx2kuaHvTiSZrvka8ThDJV9w_Wl34agDdR-tTmsQQLgN-2oJ52lrsUDV9kuWVystVhZtzlBgSJG9A-mA1&amp;t=1350e4b0"></SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/ScriptResource.axd?d=wOvoYXjrr_ptm4OVZbC27aDCx21NE0U6hMWe9AEzKLXUhhslnytqY2f5otDpZDmwkVraXylmZ1_3uZL_8dxWbs9UpiljTkBZBgMHJNs9Us96_1_EXcC1N31wgGTGSI6LePSbxnakRqEO7XuGRLhuO9GZm3Z4gPd9nd1kWOatceQBdGP6_lKD7HCI_xdyv1Vht-ER4suQPW1zmOcuqz15_z8mIS3lvm6SdZmnOqbpDU8U-gbH0&amp;t=1350e4b0"></SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/ScriptResource.axd?d=rE-Jw3RTg_KMgMdeJHd0obtrIwFnTsiPSX8qBDz0gNBmJnJ-CM1HYzIApFo-HaYPU5PrSekDsDmdXdOedkmtH2FhFYE-upoYIJJwgLdfZ4dp3OhSPA0cIyBDw9AcowZbTLCEyimpxd-ZvqdE_lRauCOOdCVSw6SKqo004gEEB3PMsRQrpaRTKWwBBdXBLDVOKRiIDxBFQyMKJeXuEDSat8MHDsM1&amp;t=1350e4b0"></SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/ScriptResource.axd?d=ktzlIto78qtJzseO1uzxdBCCI7pOSSWVP8cQp-bDdH2h_m8R4wAJmw7fPnKPV3zWakKbwHnOvO3gucryyVXcW7oMDZ233nwTzO02d78kzq0WY3SJ07IyPAw2nFvqRJxt17hWl6_1SESK4OpPIu29ABLp5kTG2tOX7EH8VhcEB76YOXk_jWGWKkLHlXhnPFB7UE7EcKzkIWiWvthEDunHqyptc6Y1&amp;t=1350e4b0"></SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/ScriptResource.axd?d=c1di9qgPHeTsRzog8ZUu8Re5MyZOR6xmGgtISuy3nPz48RRW6bBw_elQLayMl-ewrwgq9jjJOn_QOve0Jf_dsFCXSZNs4e74Ie8JnwOhzae_ksZZTE9h1ZI38VEAEN7eNPoM8zIQIqhdnALhGnthaCIJLByxzhk6Ej-M7TbAqJSxKCv653F47WBpqgS8Vl5y9Lz4zfEa1reAxxYOwGatZIh4pcM1&amp;t=1350e4b0"></SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/ScriptResource.axd?d=0IGVQBnwJZ4sCHnUcKoZm98-zmXCXN24iPWAd7E5rG0q8-W2Gv-ODTm-e4YJwKdgtjgSUl8bDAx006ROCTSCChf2hn6nQZv2Nxgo4pTVh6C5jhSjTwhPMW_yaluhP0N7DEKwOv1GqYnK8oGANzVll-VktKLuChNUoXvkt_fQYsmudszqjD1vYPjeipEi2kO3k2Qmww2&amp;t=1350e4b0"></SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/ScriptResource.axd?d=6z0lXL8lwig-Vj4OMTUwZ5-OweqLOINJsCLZ4Edse-VDDvdLRjPxCcFrstCA5AkLAxntKFnmtBhV4xLN9WDd-gIKh7cK-tB5ojN6vl-Qhl7DeynUDU8KFKbuVWLH_nutK0PUWv_-puDVZP323aJVTeb4ChaWEi2D9ybI2tcdBD8LDYFX8_8txUO7zksZGWpZiqY0A3kVb9AqGLbW_DdHlT6KRQA1&amp;t=1350e4b0"></SCRIPT>

<SCRIPT type=text/javascript src="/SITApps/SITPortal/WebResource.axd?d=UCBbb3_0JI25m_wF9I12yCOI7YJzI4eF-c2AfkO0CevVg4ZeW-HO89RzznhQyGcwirG45tqRhDzR-QwxPqKksfIriUs1&amp;t=635588903086469712"></SCRIPT>

<DIV> </DIV>
<SCRIPT language=javascript type=text/javascript>
            var vSplitterId = '';
            var hSplitterRightId = '';
            var contentId = 'content';
            var tMainId = 'tMain';
            var ModalProgress = 'ctl01_ModalProgress';
            var webTabId = '';
            var dbgTxtId = undefined;// 'txtDebug';

        </SCRIPT>

<SCRIPT type=text/javascript>
//<![CDATA[
Sys.WebForms.PageRequestManager._initialize('ctl01$ScriptManager1', document.getElementById('aspnetForm'));
Sys.WebForms.PageRequestManager.getInstance()._updateControls(['tctl01$PortalContent$BomAssembly1$WebGroupBox1$UpdatePanel1','tctl01$PortalContent$BomAssembly1$WebGroupBox1$UpdatePanel2','tctl01$PortalContent$BomAssembly1$CABConfigurableTab1$CABConfigurableTabPanel1$UpdatePanel3','tctl01$PortalContent$BomAssembly1$UpdatePanel5'], ['ctl01$PortalContent$BomAssembly1$WebGroupBox1$ddlTerminal','ctl01$PortalContent$BomAssembly1$WebGroupBox1$ddlWorkOperation'], [], 90);
//]]>
</SCRIPT>

<DIV id=container>
<DIV id=page>
<TABLE class=nav cellSpacing=0 cellPadding=0 width="100%">
<TBODY>
<TR>
<TD class=navtop style="TEXT-ALIGN: left">
<SCRIPT language=javascript type=text/javascript>
	function pageLoad(sender, args)
	{
	    var mainMenu = $find("ctl01_WindowsMenu1_CollapsiblePanelExtenderMainMenu");
	    var menu = $find("ctl01_WindowsMenu1_CollapsiblePanelExtenderMenu");
	    if (mainMenu)
	    {
		    mainMenu.add_expandComplete(showLogoutFalse);
		    mainMenu.add_collapseComplete(showLogoutTrue);
	    }
	    if (menu)
	    {
		    menu.add_expandComplete(showLogoutFalse);
		    menu.add_collapseComplete(showLogoutFalse);
	    }
	}
	function showLogoutFalse(sender, args) { showLogout(false); }
	function showLogoutTrue(sender, args) { showLogout(true); }
	function showLogout(isMain)
	{
		setACookie("CollapseMenu", isMain, null);
	    var mainMenu = $get("ctl01_WindowsMenu1_PanelMainMenuLogout");
	    if (mainMenu) mainMenu.style.display = isMain ? "block" : "none";
	    var menu = $get("ctl01_WindowsMenu1_PanelMenuLogout");
		if (menu) menu.style.display = isMain ? "none" : "block";
	}
	function setACookie(name, value, expirationDate) // not used
	{
		if (document.cookie)
		{
			if (expirationDate == null)
			{
				expirationDate = new Date();
				expirationDate.setFullYear(expirationDate.getFullYear() + 1);
			}
			document.cookie = name + "=" + escape(value) + "; expires=" + expirationDate.toGMTString();
		}
	}	
</SCRIPT>

<DIV id=ctl01_WindowsMenu1_PanelMainMenu style="BORDER-TOP: medium none; HEIGHT: auto; BORDER-RIGHT: medium none; OVERFLOW-Y: hidden; BORDER-BOTTOM: medium none; BORDER-LEFT: medium none; VISIBILITY: visible">
<DIV style="HEIGHT: auto; POSITION: ; VISIBILITY: visible">
<TABLE class=menu-bar cellSpacing=0 cellPadding=0 width="100%">
<TBODY>
<TR>
<TD style="WIDTH: 20px" align=left><IMG id=ctl01_WindowsMenu1_ToggleMainMenuImage style="BORDER-LEFT-WIDTH: 0px; BORDER-RIGHT-WIDTH: 0px; BORDER-BOTTOM-WIDTH: 0px; BORDER-TOP-WIDTH: 0px" src="../../images/uparrows_white.gif"> </TD>
<TD align=left>
<DIV class=" ig_Control igmn_Control menu-bar" style="BORDER-TOP-STYLE: none; CURSOR: default; FONT-SIZE: 12px; WIDTH: 100%; BORDER-COLLAPSE: collapse; BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; BORDER-LEFT-STYLE: none" menuframe="1">
<TABLE tabIndex=0 id=ctl01WindowsMenu1SiteMapMenu_MainM cellSpacing=3 cellPadding=0 border=0 submenu="1" _old="true">
<TBODY>
<TR>
<TD igitem="1">
<TABLE id=ctl01WindowsMenu1SiteMapMenu_1 class="igmn_TopLevelParent igmn_Parent ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igTop="1" igUrl="/SITApps/SITPortal/PortalPage/Home.aspx" igChildId="ctl01WindowsMenu1SiteMapMenu_1M" igHov="igmn_TopLevelHover ig_Hover igmn_Hover ig_a0da865d_r9 menu-item-hover" _old="true">
<TBODY>
<TR>
<TD width=1><IMG src="/SITApps/SITPortal/images/MenuBar/HomeHS.gif"></TD>
<TD align=left><NOBR>主页</NOBR></TD></TR></TBODY></TABLE></TD>
<TD igitem="1">
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2 class="igmn_TopLevelParent igmn_Parent ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igTop="1" igUrl="/SITApps/SITPortal/PortalPage/Comba/IndexProductionOperation.aspx" igChildId="ctl01WindowsMenu1SiteMapMenu_2M" igHov="igmn_TopLevelHover ig_Hover igmn_Hover ig_a0da865d_r9 menu-item-hover" _old="true">
<TBODY>
<TR>
<TD width=1></TD>
<TD align=left><NOBR>生产操作</NOBR></TD></TR></TBODY></TABLE></TD>
<TD igitem="1">
<TABLE id=ctl01WindowsMenu1SiteMapMenu_3 class="igmn_TopLevelParent igmn_Parent ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igTop="1" igUrl="/SITApps/SITPortal/PortalPage/Comba/IndexReport.aspx" igChildId="ctl01WindowsMenu1SiteMapMenu_3M" igHov="igmn_TopLevelHover ig_Hover igmn_Hover ig_a0da865d_r9 menu-item-hover" _old="true">
<TBODY>
<TR>
<TD width=1></TD>
<TD align=left><NOBR>报表</NOBR></TD></TR></TBODY></TABLE></TD></TR>
<TR style="DISPLAY: none; VISIBILITY: hidden">
<TD><SPAN id=ctl01_WindowsMenu1_SiteMapMenu style="DISPLAY: none" name="ctl01_WindowsMenu1_SiteMapMenu"></SPAN><INPUT id=ctl01$WindowsMenu1$SiteMapMenu type=hidden name=ctl01$WindowsMenu1$SiteMapMenu> </TD></TR></TBODY></TABLE></DIV>
<STYLE type=text/css></STYLE>

<DIV id=abs_ctl01WindowsMenu1SiteMapMenu style="DISPLAY: none">
<DIV style="OVERFLOW: hidden; POSITION: absolute; Z-INDEX: 12000; DISPLAY: none; VISIBILITY: hidden" container="1">
<DIV id=ctl01WindowsMenu1SiteMapMenu_1M class=" igmn_Island  igmn_Island menu-bar" style="POSITION: relative" submenu="1">
<DIV scrollDiv="1">
<TABLE class=" igmn_Island  igmn_Island menu-bar" style="BORDER-LEFT-WIDTH: 0px; BORDER-RIGHT-WIDTH: 0px; BORDER-BOTTOM-WIDTH: 0px; BORDER-COLLAPSE: collapse; POSITION: relative; BORDER-TOP-WIDTH: 0px" cellSpacing=0 cellPadding=2 border=0>
<TBODY>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_1_1 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/MemberLogin.aspx">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MenuBar/ProtectFormHS.gif"></TD>
<TD igtxt="1"><NOBR>登录</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_1_2 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/MyProfile.aspx">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MenuBar/MyProfile.gif"></TD>
<TD igtxt="1"><NOBR>我的配置文件</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_1_3 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/MemberChangePassword.aspx">
<TBODY>
<TR>
<TD width=25></TD>
<TD igtxt="1"><NOBR>更改密码</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR></TBODY></TABLE></DIV></DIV></DIV>
<DIV style="OVERFLOW: hidden; POSITION: absolute; Z-INDEX: 12000; DISPLAY: none; VISIBILITY: hidden" container="1">
<DIV id=ctl01WindowsMenu1SiteMapMenu_2M class=" igmn_Island  igmn_Island menu-bar" style="POSITION: relative" submenu="1">
<DIV scrollDiv="1">
<TABLE class=" igmn_Island  igmn_Island menu-bar" style="BORDER-LEFT-WIDTH: 0px; BORDER-RIGHT-WIDTH: 0px; BORDER-BOTTOM-WIDTH: 0px; BORDER-COLLAPSE: collapse; POSITION: relative; BORDER-TOP-WIDTH: 0px" cellSpacing=0 cellPadding=2 border=0>
<TBODY>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_1 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Electronics/Production/Inspect.aspx">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Library/Production_Client_32.ico"></TD>
<TD igtxt="1"><NOBR>质量客户端</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_2 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/BomAssembly.aspx">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/ProductionOperation/Simple_Production_Client.ico"></TD>
<TD igtxt="1"><NOBR>精简生产客户端</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3 class=" igmn_Parent ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/IndexNote.aspx" igChildId="ctl01WindowsMenu1SiteMapMenu_2_3M">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/Note_Management.ico"></TD>
<TD igtxt="1"><NOBR>备注管理</NOBR> </TD>
<TD width=15><IMG src="../../images/MechatronicsLib/ig_menuTri.gif" align=right> </TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_4 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/SNLinkForCustmer.aspx">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/ProductionOperation/Link_Internal_and_External.ico"></TD>
<TD igtxt="1"><NOBR>内外序列号关联</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_5 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/SNLinkForRebuild.aspx">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/ProductionOperation/Rebuild_Link.ico"></TD>
<TD igtxt="1"><NOBR>改造维修拆零序列号关联</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_6 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/SNLinkForMac.aspx">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/ProductionOperation/Link_MAC.ico"></TD>
<TD igtxt="1"><NOBR>序列号MAC地址关联</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_7 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Electronics/Production/EquipmentSetup.aspx">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/Electronics/PcbInspect.gif"></TD>
<TD igtxt="1"><NOBR>设备上料</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR></TBODY></TABLE></DIV></DIV></DIV>
<DIV style="OVERFLOW: hidden; POSITION: absolute; Z-INDEX: 12000; DISPLAY: none; VISIBILITY: hidden" container="1">
<DIV id=ctl01WindowsMenu1SiteMapMenu_2_3M class=" igmn_Island  igmn_Island menu-bar" style="POSITION: relative" submenu="1">
<DIV scrollDiv="1">
<TABLE class=" igmn_Island  igmn_Island menu-bar" style="BORDER-LEFT-WIDTH: 0px; BORDER-RIGHT-WIDTH: 0px; BORDER-BOTTOM-WIDTH: 0px; BORDER-COLLAPSE: collapse; POSITION: relative; BORDER-TOP-WIDTH: 0px" cellSpacing=0 cellPadding=2 border=0>
<TBODY>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_1 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=Order">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>工单备注</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_2 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=CWYZ1SerialNumber">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>整机一部序列号备注</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_3 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=CWYZ2SerialNumber">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>整机二部序列号备注</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_4 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=CWYZ3SerialNumber">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>整机三部序列号备注</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_5 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=CWJSerialNumber">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>无传接序列号备注</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_6 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=CWCSerialNumber">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>无传输序列号备注</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_7 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=CSPSerialNumber">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>射频序列号备注(历史记录)</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_8 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=CGFSerialNumber">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>功放序列号备注</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_9 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=CWYBSerialNumber">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>无优部件序列号备注</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_10 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=CTX1SerialNumber">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>天线一部序列号备注(历史记录)</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_11 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=CTX2SerialNumber">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>天线二部序列号备注(历史记录)</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_12 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=CTX3SerialNumber">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>天线三部序列号备注(历史记录)</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_13 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=CTX4SerialNumber">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>天线四部序列号备注(历史记录)</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_14 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=CTX5SerialNumber">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>天线五部序列号备注(历史记录)</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_15 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=RCUSerialNumber">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>RCU序列号备注</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_16 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=CTX6SerialNumber">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>天线六部序列号备注(历史记录)</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_17 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=RSAUTOSerialNumber">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>回流焊/自动化序列号备注</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_18 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=CWJSerialNumber2">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>无传接序列号备注2</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_19 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=CTXRSAUTOSerialNumber">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>天线\回流焊（单个）序列号备注</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_20 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=CTXSerialNumber">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>天线生产部</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_21 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=CSP2SerialNumber">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>射频部件部工单备注</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_22 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/Note/Remark.aspx?ReferrerUrl=~/PortalPage/Comba/note/Remark.aspx,NoteType=WavelabSerialNumber">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Note/SN_Note.ico"></TD>
<TD igtxt="1"><NOBR>波达序列号备注</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR></TBODY></TABLE></DIV></DIV></DIV>
<DIV style="OVERFLOW: hidden; POSITION: absolute; Z-INDEX: 12000; DISPLAY: none; VISIBILITY: hidden" container="1">
<DIV id=ctl01WindowsMenu1SiteMapMenu_3M class=" igmn_Island  igmn_Island menu-bar" style="POSITION: relative" submenu="1">
<DIV scrollDiv="1">
<TABLE class=" igmn_Island  igmn_Island menu-bar" style="BORDER-LEFT-WIDTH: 0px; BORDER-RIGHT-WIDTH: 0px; BORDER-BOTTOM-WIDTH: 0px; BORDER-COLLAPSE: collapse; POSITION: relative; BORDER-TOP-WIDTH: 0px" cellSpacing=0 cellPadding=2 border=0>
<TBODY>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_3_1 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Electronics/Reports/SNReport.aspx">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/Electronics/SNReport_16x16.png"></TD>
<TD igtxt="1"><NOBR>序列号报表</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_3_2 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igUrl="/SITApps/SITPortal/PortalPage/Comba/OrderReport.aspx">
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Report/Order_Report.ico"></TD>
<TD igtxt="1"><NOBR>工单报表</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR></TBODY></TABLE></DIV></DIV></DIV></DIV></TD>
<TD id=ctl01_WindowsMenu1_PanelMainMenuLogout style="DISPLAY: none" align=right><SPAN id=ctl01_WindowsMenu1_UserName style="FONT-SIZE: 0.9em; FONT-FAMILY: Verdana; FONT-WEIGHT: bold">cenjianxun</SPAN> <SPAN id=ctl01_WindowsMenu1_LabelSeparator style="FONT-SIZE: 0.9em; FONT-FAMILY: Verdana; FONT-WEIGHT: bold">|</SPAN> <A id=ctl01_WindowsMenu1_LinkButtonLogout style="FONT-SIZE: 0.9em; FONT-FAMILY: Verdana; COLOR: gray" href="javascript:__doPostBack('ctl01$WindowsMenu1$LinkButtonLogout','')">退出</A> </TD>
<TD style="WIDTH: 20px" align=right>&nbsp;</TD></TR></TBODY></TABLE></DIV></DIV>
<DIV id=ctl01_WindowsMenu1_PanelMenu style="BORDER-TOP: medium none; HEIGHT: auto; BORDER-RIGHT: medium none; OVERFLOW-Y: hidden; BORDER-BOTTOM: medium none; BORDER-LEFT: medium none; VISIBILITY: visible">
<DIV style="HEIGHT: auto; POSITION: ; VISIBILITY: visible"><!-- CssClass="navtop" -->
<TABLE cellSpacing=0 cellPadding=0 width="100%">
<TBODY>
<TR>
<TD style="WIDTH: 20px" align=left><IMG id=ctl01_WindowsMenu1_ToggleWindowsMenuImage style="BORDER-LEFT-WIDTH: 0px; BORDER-RIGHT-WIDTH: 0px; BORDER-BOTTOM-WIDTH: 0px; BORDER-TOP-WIDTH: 0px" src="../../images/uparrows_white.gif"> </TD>
<TD align=left><SPAN id=ctl01_WindowsMenu1_CABSiteMapPath1 class=sitemap style="FONT-SIZE: 0.8em; FONT-FAMILY: Verdana"><A href="#ctl01_WindowsMenu1_CABSiteMapPath1_SkipLink"><IMG style="BORDER-LEFT-WIDTH: 0px; BORDER-RIGHT-WIDTH: 0px; BORDER-BOTTOM-WIDTH: 0px; BORDER-TOP-WIDTH: 0px" alt=跳过导航链接 src="/SITApps/SITPortal/WebResource.axd?d=Hsv2hREvu2npIctgSNkMy_4Wxvl8JxyUtgSXXXX5rEBMRO88Roi7ubaHpX37BJwoS-K3k8anGYiB930ymG9Q6-WCTCY1&amp;t=635588903086469712" width=0 height=0></A><SPAN id=ctl01_WindowsMenu1_CABSiteMapPath1_ctl00><A id=ctl01_WindowsMenu1_CABSiteMapPath1_ctl00_ctl00 title=生产操作 href="/SITApps/SITPortal/PortalPage/Comba/IndexProductionOperation.aspx">生产操作</A></SPAN><SPAN id=ctl01_WindowsMenu1_CABSiteMapPath1_ctl01>:</SPAN><SPAN id=ctl01_WindowsMenu1_CABSiteMapPath1_ctl02><A id=ctl01_WindowsMenu1_CABSiteMapPath1_ctl02_ctl00 title=生产操作 href="/SITApps/SITPortal/PortalPage/Comba/IndexProductionOperation.aspx">生产操作</A></SPAN><SPAN id=ctl01_WindowsMenu1_CABSiteMapPath1_ctl03>:</SPAN><SPAN id=ctl01_WindowsMenu1_CABSiteMapPath1_ctl04>精简生产客户端</SPAN><A id=ctl01_WindowsMenu1_CABSiteMapPath1_SkipLink></A></SPAN> </TD>
<TD id=ctl01_WindowsMenu1_PanelMenuLogout align=right><SPAN id=ctl01_WindowsMenu1_UserName2 style="FONT-SIZE: 0.9em; FONT-FAMILY: Verdana; FONT-WEIGHT: bold">cenjianxun</SPAN> <SPAN id=ctl01_WindowsMenu1_LabelSeparator2 style="FONT-SIZE: 0.9em; FONT-FAMILY: Verdana; FONT-WEIGHT: bold">|</SPAN> <A id=ctl01_WindowsMenu1_LinkButtonLogout2 style="FONT-SIZE: 0.9em; FONT-FAMILY: Verdana; COLOR: gray" href="javascript:__doPostBack('ctl01$WindowsMenu1$LinkButtonLogout2','')">退出</A> </TD>
<TD style="WIDTH: 20px" align=right>&nbsp;</TD></TR></TBODY></TABLE></DIV></DIV><INPUT id=ctl01_WindowsMenu1_CollapsiblePanelExtenderMainMenu_ClientState type=hidden value=false name=ctl01$WindowsMenu1$CollapsiblePanelExtenderMainMenu_ClientState> <INPUT id=ctl01_WindowsMenu1_CollapsiblePanelExtenderMenu_ClientState type=hidden value=false name=ctl01$WindowsMenu1$CollapsiblePanelExtenderMenu_ClientState> </TD></TR></TBODY></TABLE>
<DIV class=fullsize><LINK rel=Stylesheet type=text/css href="../../App_Themes/CombaTheme/Comba.css" visible="false">
<SCRIPT type=text/javascript>
    function EnterTextBox(button) {
        if (event.keyCode == 13 && document.all["ctl01_PortalContent_BomAssembly1_WebGroupBox1_txtSn"].value != "") {
            event.keyCode = 9;
            event.returnValue = false;
            document.all["ctl01_PortalContent_BomAssembly1_WebGroupBox1_btnScan"].click();
        }
    }

    function EnterTextBox1(button) {
        if (event.keyCode == 13 && document.all["ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_CABConfigurableTabPanel1_txtSubSn"].value != "") {
            event.keyCode = 9;
            event.returnValue = false;
            document.all["ctl01_PortalContent_BomAssembly1_btnKeyPress"].click();
        }
    }

    function EnterTextBox2(button) {
        if (event.keyCode == 13 && document.all["ctl01_PortalContent_BomAssembly1_WebGroupBox1_txtDisassemblySerialNumber"].value != "") {
            event.keyCode = 9;
            event.returnValue = false;
            document.all["ctl01_PortalContent_BomAssembly1_WebGroupBox1_btnDisAssemblySn"].click();
        }
    }

    function test() {
        if (confirm("确认把序列号[" + document.all["ctl01_PortalContent_BomAssembly1_WebGroupBox1_txtDisassemblySerialNumber"].value + "]从主部件上拆掉吗？")) {
            return true;
        }
        return false;
    }

    //    try {
    //        var obj = new ActiveXObject("WScript.Network");
    //    } catch (e) {
    //    alert(e);
    //    }
    //   function GetComputerName() {
    //       document.getElementById("ctl01_PortalContent_BomAssembly1_lblComputerName").value = obj.ComputerName;
    //   }
    //   window.onload = GetComputerName();
</SCRIPT>

<TABLE width="100%">
<TBODY>
<TR>
<TD>
<TABLE width="100%">
<TBODY>
<TR>
<TD>
<TABLE width="100%">
<TBODY>
<TR>
<TD class=CABReportPageHeader width="50%" align=left><SPAN id=ctl01_PortalContent_BomAssembly1_LblSepatatorText>精简生产客户端</SPAN> </TD>
<TD width="47%" align=right></TD>
<TD width="3%" align=right></TD>
<TD><IMG id=TitleImage style="BORDER-LEFT-WIDTH: 0px; BORDER-RIGHT-WIDTH: 0px; BORDER-BOTTOM-WIDTH: 0px; BORDER-TOP-WIDTH: 0px" src="../../Images/MechatronicsLib/Siemens-logo.jpg"> </TD></TR></TBODY></TABLE></TD></TR></TBODY></TABLE></TD></TR></TBODY></TABLE>
<TABLE width="100%">
<TBODY>
<TR>
<TD>
<HR>
</TD></TR>
<TR>
<TD>
<TABLE width="80%" align=center>
<TBODY>
<TR>
<TD>
<TABLE id=ctl01_PortalContent_BomAssembly1_leftTable style="WIDTH: 100%" border=0>
<TBODY>
<TR id=ctl01_PortalContent_BomAssembly1_leftTableRow>
<TD id=ctl01_PortalContent_BomAssembly1_leftTableCell>
<FIELDSET id=ctl01_PortalContent_BomAssembly1_WebGroupBox1 class="iggrpbxbrdr iggrpbxctl ctl01PortalContentBomAssembly1WebGroupBox1ctl iggrpbxbrdr">
<DIV style="HEIGHT: 100%; WIDTH: 100%; FLOAT: left">
<TABLE style="WIDTH: 100%" border=0>
<TBODY>
<TR>
<TD>
<DIV id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_UpdatePanel1>
<TABLE id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_leftSubTable style="WIDTH: 100%" border=0>
<TBODY>
<TR id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_leftSubTableRow>
<TD id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_leftSubTableCell style="WIDTH: 25%"><SPAN id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_lblTerminal>工作站点</SPAN></TD>
<TD id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_TableCell1 style="WIDTH: 75%"><SELECT onchange="javascript:setTimeout('__doPostBack(\'ctl01$PortalContent$BomAssembly1$WebGroupBox1$ddlTerminal\',\'\')', 0)" id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_ddlTerminal style="WIDTH: 90%" name=ctl01$PortalContent$BomAssembly1$WebGroupBox1$ddlTerminal></SELECT></TD></TR>
<TR id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_TableRow1>
<TD id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_TableCell2 style="WIDTH: 25%"><SPAN id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_Label1>工艺点</SPAN></TD>
<TD id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_TableCell3 style="WIDTH: 75%"><SELECT onchange="javascript:setTimeout('__doPostBack(\'ctl01$PortalContent$BomAssembly1$WebGroupBox1$ddlWorkOperation\',\'\')', 0)" id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_ddlWorkOperation style="WIDTH: 90%" name=ctl01$PortalContent$BomAssembly1$WebGroupBox1$ddlWorkOperation></SELECT></TD></TR></TBODY></TABLE></DIV></TD></TR>
<TR>
<TD>
<HR>
</TD></TR>
<TR>
<TD>
<DIV id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_UpdatePanel2>
<TABLE id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_leftBottomTable style="WIDTH: 100%" border=0>
<TBODY>
<TR>
<TD style="WIDTH: 25%"><SPAN id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_Label2>序列号：</SPAN></TD>
<TD style="WIDTH: 50%" colSpan=2><INPUT onkeypress="EnterTextBox('btnScan')" onfocus=javascript:this.select() id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_txtSn style="BORDER-TOP: #7c7c94 1px solid; BORDER-RIGHT: #7c7c94 1px solid; WIDTH: 90%; BORDER-BOTTOM: #7c7c94 1px solid; TEXT-TRANSFORM: uppercase; BORDER-LEFT: #7c7c94 1px solid; BACKGROUND-COLOR: whitesmoke" name=ctl01$PortalContent$BomAssembly1$WebGroupBox1$txtSn></TD>
<TD style="WIDTH: 25%"><A id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_lbtnSnReport href="javascript:__doPostBack('ctl01$PortalContent$BomAssembly1$WebGroupBox1$lbtnSnReport','')">序列号报表</A></TD></TR>
<TR id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_TableRow3>
<TD id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_TableCell5 style="WIDTH: 25%"><SPAN id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_lblDisAssemblySN>拆卸序列号：</SPAN></TD>
<TD id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_TableCell6 style="WIDTH: 50%" colSpan=2><INPUT onkeypress="EnterTextBox2('btnDisAssemblySn')" onfocus=javascript:this.select() id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_txtDisassemblySerialNumber style="BORDER-TOP: #7c7c94 1px solid; BORDER-RIGHT: #7c7c94 1px solid; WIDTH: 90%; BORDER-BOTTOM: #7c7c94 1px solid; TEXT-TRANSFORM: uppercase; BORDER-LEFT: #7c7c94 1px solid; BACKGROUND-COLOR: whitesmoke" name=ctl01$PortalContent$BomAssembly1$WebGroupBox1$txtDisassemblySerialNumber></TD>
<TD id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_TableCell7 style="WIDTH: 25%"><SPAN id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_lblDisAssemblySnDescription>(仅针对关键物料拆卸)</SPAN></TD></TR>
<TR>
<TD style="WIDTH: 25%"><SPAN id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_Label3>工单号：</SPAN></TD>
<TD style="WIDTH: 50%" colSpan=2><INPUT disabled id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_txtOrder style="BORDER-TOP: #7c7c94 1px solid; BORDER-RIGHT: #7c7c94 1px solid; WIDTH: 90%; BORDER-BOTTOM: #7c7c94 1px solid; BORDER-LEFT: #7c7c94 1px solid; BACKGROUND-COLOR: whitesmoke" readOnly name=ctl01$PortalContent$BomAssembly1$WebGroupBox1$txtOrder></TD>
<TD style="WIDTH: 25%" vAlign=middle rowSpan=2><SPAN id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_lblCount style="FONT-SIZE: xx-large; FONT-WEIGHT: bold; COLOR: red">0</SPAN> &nbsp; <SPAN id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_Label7>(该工单下序列号在该工艺点的过站数量)</SPAN></TD></TR>
<TR>
<TD style="WIDTH: 25%"><SPAN id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_Label4>工单数量：</SPAN></TD>
<TD style="WIDTH: 50%" colSpan=2><INPUT disabled id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_txtOrderQty style="BORDER-TOP: #7c7c94 1px solid; BORDER-RIGHT: #7c7c94 1px solid; WIDTH: 90%; BORDER-BOTTOM: #7c7c94 1px solid; BORDER-LEFT: #7c7c94 1px solid; BACKGROUND-COLOR: whitesmoke" readOnly name=ctl01$PortalContent$BomAssembly1$WebGroupBox1$txtOrderQty></TD></TR>
<TR>
<TD style="WIDTH: 25%"><SPAN id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_lblOrderNote>SAP 作业单备注：</SPAN></TD>
<TD style="WIDTH: 75%" colSpan=3><INPUT disabled id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_txtOrderNote style="BORDER-TOP: #7c7c94 1px solid; BORDER-RIGHT: #7c7c94 1px solid; WIDTH: 90%; BORDER-BOTTOM: #7c7c94 1px solid; BORDER-LEFT: #7c7c94 1px solid; BACKGROUND-COLOR: whitesmoke" readOnly name=ctl01$PortalContent$BomAssembly1$WebGroupBox1$txtOrderNote></TD></TR>
<TR>
<TD style="WIDTH: 25%"><SPAN id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_Label5>产品物料编码：</SPAN></TD>
<TD style="WIDTH: 75%" colSpan=3><INPUT disabled id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_txtMaterialID style="BORDER-TOP: #7c7c94 1px solid; BORDER-RIGHT: #7c7c94 1px solid; WIDTH: 90%; BORDER-BOTTOM: #7c7c94 1px solid; BORDER-LEFT: #7c7c94 1px solid; BACKGROUND-COLOR: whitesmoke" readOnly name=ctl01$PortalContent$BomAssembly1$WebGroupBox1$txtMaterialID></TD></TR>
<TR>
<TD style="WIDTH: 25%"><SPAN id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_Label6>产品物料描述：</SPAN></TD>
<TD style="WIDTH: 75%" colSpan=3><INPUT disabled id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_txtMaterialDescript style="BORDER-TOP: #7c7c94 1px solid; BORDER-RIGHT: #7c7c94 1px solid; WIDTH: 90%; BORDER-BOTTOM: #7c7c94 1px solid; BORDER-LEFT: #7c7c94 1px solid; BACKGROUND-COLOR: whitesmoke" readOnly name=ctl01$PortalContent$BomAssembly1$WebGroupBox1$txtMaterialDescript></TD></TR>
<TR>
<TD style="WIDTH: 100%" colSpan=4>
<TABLE style="WIDTH: 100%" border=0>
<TBODY>
<TR>
<TD id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_TableCell8 style="WIDTH: 33%"><INPUT id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_btnScan class=btn style="WIDTH: 90%" type=submit value=扫描 name=ctl01$PortalContent$BomAssembly1$WebGroupBox1$btnScan></TD>
<TD id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_TableCell9 style="WIDTH: 33%"><INPUT onclick="javascript:return test();" id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_btnDisAssemblySn class=btn style="WIDTH: 90%" type=submit value=拆卸序列号 name=ctl01$PortalContent$BomAssembly1$WebGroupBox1$btnDisAssemblySn></TD>
<TD id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_TableCell10 style="WIDTH: 33%"><INPUT id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_btnReset class=btn style="WIDTH: 90%" type=submit value=重置 name=ctl01$PortalContent$BomAssembly1$WebGroupBox1$btnReset></TD></TR></TBODY></TABLE></TD></TR></TBODY></TABLE></DIV></TD></TR></TBODY></TABLE></DIV></FIELDSET> 
<STYLE type=text/css>.ctl01PortalContentBomAssembly1WebGroupBox1ctl {
	WIDTH: 100%
}
</STYLE>
</TD></TR></TBODY></TABLE></TD></TR></TBODY></TABLE></TD></TR>
<TR>
<TD>
<HR>
</TD></TR>
<TR>
<TD>
<TABLE width="80%" align=center>
<TBODY>
<TR>
<TD>
<DIV id=ctl01_PortalContent_BomAssembly1_CABConfigurableTab1 class="ajax__tab_xp ajax__tab_container ajax__tab_default" style="WIDTH: 100%; VISIBILITY: visible" FriendlyName="" ControlGuid="c46b42a0-680d-4b81-acf4-6612272aae52">
<DIV id=ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_header class=ajax__tab_header><SPAN id=ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_CABConfigurableTabPanel1_tab class=ajax__tab_active><SPAN class=ajax__tab_outer><SPAN class=ajax__tab_inner><SPAN id=__tab_ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_CABConfigurableTabPanel1 class=ajax__tab_tab><SPAN id=ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_CABConfigurableTabPanel1_Label8>组装</SPAN> </SPAN></SPAN></SPAN></SPAN></DIV>
<DIV id=ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_body class=ajax__tab_body>
<DIV id=ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_CABConfigurableTabPanel1 class=ajax__tab_panel>
<TABLE id=ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_CABConfigurableTabPanel1_tabTable style="WIDTH: 100%" border=0>
<TBODY>
<TR id=ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_CABConfigurableTabPanel1_TableRow2>
<TD id=ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_CABConfigurableTabPanel1_TableCell4>
<TABLE id=ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_CABConfigurableTabPanel1_rightTable style="WIDTH: 100%" border=0>
<TBODY>
<TR>
<TD>
<DIV id=ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_CABConfigurableTabPanel1_UpdatePanel3></DIV></TD></TR></TBODY></TABLE></TD></TR></TBODY></TABLE></DIV></DIV></DIV></TD></TR></TBODY></TABLE></TD></TR></TBODY></TABLE>
<DIV id=ctl01_PortalContent_BomAssembly1_UpdatePanel5><INPUT id=ctl01_PortalContent_BomAssembly1_btnKeyPress style="DISPLAY: none" type=submit value=keyPress name=ctl01$PortalContent$BomAssembly1$btnKeyPress> </DIV></DIV></DIV>
<DIV id=WaitPanelDiv class=WaitPanel>
<DIV id=ctl01_UpdateProgress1 style="DISPLAY: none">
<DIV id=ctl01_PanelWait class=PanelWait style="BORDER-TOP: #222222 2px groove; HEIGHT: 50px; BORDER-RIGHT: #222222 2px groove; WIDTH: 250px; BORDER-BOTTOM: #222222 2px groove; BORDER-LEFT: #222222 2px groove"><IMG id=ctl01_ImageWait style="BORDER-LEFT-WIDTH: 0px; BORDER-RIGHT-WIDTH: 0px; BORDER-BOTTOM-WIDTH: 0px; BORDER-TOP-WIDTH: 0px" src="../../images/spinner.gif" align=left> 
<DIV style="TEXT-ALIGN: center"><SPAN id=ctl01_LabelWait style="FONT-SIZE: large; HEIGHT: 39px; WIDTH: 188px; DISPLAY: inline-block">进行中... 请等待.</SPAN></DIV></DIV></DIV>
<DIV id=ctl01_panelUpdateProgress class=UpdateProgressBackground style="POSITION: fixed; LEFT: 798px; Z-INDEX: 10001; DISPLAY: none; TOP: 381px"></DIV>
<DIV id=ctl01_ModalProgress_backgroundElement class=modalBackground style="HEIGHT: 778px; WIDTH: 1597px; POSITION: fixed; LEFT: 0px; Z-INDEX: 10000; DISPLAY: none; TOP: 0px"></DIV></DIV></DIV>
<SCRIPT type=text/javascript>
        //<![CDATA[
        function AddClientTag(){
            var obj = document.getElementsByTagName('body')[0]; 
            if (obj != null) {
                obj.insertAdjacentHTML('afterBegin', "<object id='SITCABTool' classid='CLSID:FA7AC8C3-9080-4CA3-B5DA-3800FFF534EF' codebase='http://192.168.32.166/CABINET/SITCABTools.cab'></object>");
                }
            }
        AddClientTag();
        function UpdateClientInfo() {
            var obj = document.getElementById('SITCABTool');
            if( obj != null ) {
                try
                    {
                    var computerName = obj.GetHostName();     
                    PageMethods.UpdateComputerName(computerName, SuccessUpdate, FailureUpdate);
                    }
                catch( e )
                    {
                       
                    }
                }          
            }
        UpdateClientInfo();

        function SuccessUpdate(data) {};
        function FailureUpdate(data) {};
        //]]>
        </SCRIPT>

<SCRIPT type=text/javascript>
//<![CDATA[
WebForm_AutoFocus('ctl01_PortalContent_BomAssembly1_WebGroupBox1_txtSn');Sys.Application.initialize();
//]]>
</SCRIPT>

<SCRIPT type=text/javascript>
//<![CDATA[
igmenu_ctl01WindowsMenu1SiteMapMenu_Menu=[ "ctl01$WindowsMenu1$SiteMapMenu",1,1,"","ig_Hover igmn_Hover ig_a0da865d_r9 menu-item-hover","ig_Selected igmn_TopSelected ig_a0da865d_r11 menu-item-top-selected","../../images/MechatronicsLib/ig_menuTri.gif",false,"300","100","GradientWipe","#D3D3D3","5","200","1000","","","ig_Disabled igmn_Disabled ig_a0da865d_r12","ig_Item igmn_Item ig_a0da865d_r2 menu-item-top","../../images/ig_menu_scrollup.gif","../../images/ig_menu_scrollup_disabled.gif","../../images/ig_menu_scrolldown.gif","../../images/ig_menu_scrolldown_disabled.gif",false,true,"","",true,"ig_Header igmn_Header",false,true,false];

igmenu_ctl01WindowsMenu1SiteMapMenu_Events = [ ["",0],["",0],["",0],["",0],["",0]];

	igmenu_initMenu('ctl01WindowsMenu1SiteMapMenu');
//]]>
</SCRIPT>

<SCRIPT type=text/javascript>
//<![CDATA[
Sys.Application.add_init(function() {
    $create(AjaxControlToolkit.CollapsiblePanelBehavior, {"ClientStateFieldID":"ctl01_WindowsMenu1_CollapsiblePanelExtenderMainMenu_ClientState","CollapseControlID":"ctl01_WindowsMenu1_ToggleMainMenuImage","CollapsedImage":"../../images/downarrows_white.gif","ExpandControlID":"ctl01_WindowsMenu1_ToggleMainMenuImage","ExpandedImage":"../../images/uparrows_white.gif","ImageControlID":"ctl01_WindowsMenu1_ToggleMainMenuImage","SuppressPostBack":true,"id":"ctl01_WindowsMenu1_CollapsiblePanelExtenderMainMenu"}, null, null, $get("ctl01_WindowsMenu1_PanelMenu"));
});
Sys.Application.add_init(function() {
    $create(AjaxControlToolkit.CollapsiblePanelBehavior, {"ClientStateFieldID":"ctl01_WindowsMenu1_CollapsiblePanelExtenderMenu_ClientState","CollapseControlID":"ctl01_WindowsMenu1_ToggleWindowsMenuImage","CollapsedImage":"../../images/downarrows_white.gif","ExpandControlID":"ctl01_WindowsMenu1_ToggleWindowsMenuImage","ExpandedImage":"../../images/uparrows_white.gif","ImageControlID":"ctl01_WindowsMenu1_ToggleWindowsMenuImage","SuppressPostBack":true,"id":"ctl01_WindowsMenu1_CollapsiblePanelExtenderMenu"}, null, null, $get("ctl01_WindowsMenu1_PanelMainMenu"));
});
Sys.Application.add_init(function() {
    $create(AjaxControlToolkit.TabPanel, {"headerTab":$get("__tab_ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_CABConfigurableTabPanel1"),"ownerID":"ctl01_PortalContent_BomAssembly1_CABConfigurableTab1"}, null, {"owner":"ctl01_PortalContent_BomAssembly1_CABConfigurableTab1"}, $get("ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_CABConfigurableTabPanel1"));
});
Sys.Application.add_init(function() {
    $create(Siemens.SimaticIT.ConfGUIFramework.Controls.CABConfigurableTab, {"activeTabIndex":0,"clientStateField":$get("ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_ClientState")}, null, null, $get("ctl01_PortalContent_BomAssembly1_CABConfigurableTab1"));
});
Sys.Application.add_init(function() {
    $create(Sys.UI._UpdateProgress, {"associatedUpdatePanelId":null,"displayAfter":100,"dynamicLayout":true}, null, null, $get("ctl01_UpdateProgress1"));
});
Sys.Application.add_init(function() {
    $create(AjaxControlToolkit.ModalPopupBehavior, {"BackgroundCssClass":"modalBackground","PopupControlID":"ctl01_panelUpdateProgress","dynamicServicePath":"/SITApps/SITPortal/PortalPage/Comba/BomAssembly.aspx","id":"ctl01_ModalProgress"}, null, null, $get("ctl01_panelUpdateProgress"));
});
//]]>
</SCRIPT>
</FORM></BODY></HTML>