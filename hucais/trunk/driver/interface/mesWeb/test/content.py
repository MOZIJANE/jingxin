import sys

sec1 = '''<HTML xmlns="http://www.w3.org/1999/xhtml"><HEAD id=ctl01_ctl00><META content="IE=7.0000" http-equiv="X-UA-Compatible">
<TITLE>SIMATIC IT 门户网站</TITLE>
<META id=ctl01_ctl01 content=IE=EmulateIE7 http-equiv=X-UA-Compatible>
<META name=description content="SIMATIC IT 门户网站">
<META name=keywords content="SIMATIC IT, ASP.NET 2.0, MES">
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

<SCRIPT type=text/javascript src="js/jquery-1.6.1.min.js"></SCRIPT>

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
<TD style="WIDTH: 20px" align=left><IMG id=ctl01_WindowsMenu1_ToggleMainMenuImage style="BORDER-LEFT-WIDTH: 0px; BORDER-RIGHT-WIDTH: 0px; BORDER-BOTTOM-WIDTH: 0px; BORDER-TOP-WIDTH: 0px" > </TD>
<TD align=left>
<DIV class=" ig_Control igmn_Control menu-bar" style="BORDER-TOP-STYLE: none; CURSOR: default; FONT-SIZE: 12px; WIDTH: 100%; BORDER-COLLAPSE: collapse; BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; BORDER-LEFT-STYLE: none" menuframe="1">
<TABLE tabIndex=0 id=ctl01WindowsMenu1SiteMapMenu_MainM cellSpacing=3 cellPadding=0 border=0 submenu="1" _old="true">
<TBODY>
<TR>
<TD igitem="1">
<TABLE id=ctl01WindowsMenu1SiteMapMenu_1 class="igmn_TopLevelParent igmn_Parent ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igTop="1" igChildId="ctl01WindowsMenu1SiteMapMenu_1M" igHov="igmn_TopLevelHover ig_Hover igmn_Hover ig_a0da865d_r9 menu-item-hover" _old="true">
<TBODY>
<TR>
<TD width=1><IMG src="/SITApps/SITPortal/images/MenuBar/HomeHS.gif"></TD>
<TD align=left><NOBR>主页</NOBR></TD></TR></TBODY></TABLE></TD>
<TD igitem="1">
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2 class="igmn_TopLevelParent igmn_Parent ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igTop="1" igChildId="ctl01WindowsMenu1SiteMapMenu_2M" igHov="igmn_TopLevelHover ig_Hover igmn_Hover ig_a0da865d_r9 menu-item-hover" _old="true">
<TBODY>
<TR>
<TD width=1></TD>
<TD align=left><NOBR>生产操作</NOBR></TD></TR></TBODY></TABLE></TD>
<TD igitem="1">
<TABLE id=ctl01WindowsMenu1SiteMapMenu_3 class="igmn_TopLevelParent igmn_Parent ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" igTop="1" igChildId="ctl01WindowsMenu1SiteMapMenu_3M" igHov="igmn_TopLevelHover ig_Hover igmn_Hover ig_a0da865d_r9 menu-item-hover" _old="true">
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
<TABLE id=ctl01WindowsMenu1SiteMapMenu_1_1 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%">
<TBODY>
<TR>
<TD width=25><IMG src=""></TD>
<TD igtxt="1"><NOBR>登录</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_1_2 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" >
<TBODY>
<TR>
<TD width=25><IMG src=""></TD>
<TD igtxt="1"><NOBR>我的配置文件</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_1_3 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" >
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
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_1 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" >
<TBODY>
<TR>
<TD width=25><IMG src="/SITApps/SITPortal/images/MES_COMBA_Icon/Library/Production_Client_32.ico"></TD>
<TD igtxt="1"><NOBR>质量客户端</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_2 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" >
<TBODY>
<TR>
<TD width=25><IMG src=""></TD>
<TD igtxt="1"><NOBR>精简生产客户端</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3 class=" igmn_Parent ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%"  igChildId="ctl01WindowsMenu1SiteMapMenu_2_3M">
<TBODY>
<TR>
<TD width=25><IMG src=""></TD>
<TD igtxt="1"><NOBR>备注管理</NOBR> </TD>
<TD width=15><IMG src="" align=right> </TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_4 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" >
<TBODY>
<TR>
<TD width=25><IMG src=""></TD>
<TD igtxt="1"><NOBR>内外序列号关联</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_5 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" >
<TBODY>
<TR>
<TD width=25><IMG src=""></TD>
<TD igtxt="1"><NOBR>改造维修拆零序列号关联</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_6 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" >
<TBODY>
<TR>
<TD width=25><IMG src=""></TD>
<TD igtxt="1"><NOBR>序列号MAC地址关联</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_7 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" >
<TBODY>
<TR>
<TD width=25><IMG src=""></TD>
<TD igtxt="1"><NOBR>设备上料</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR></TBODY></TABLE></DIV></DIV></DIV>
<DIV style="OVERFLOW: hidden; POSITION: absolute; Z-INDEX: 12000; DISPLAY: none; VISIBILITY: hidden" container="1">
<DIV id=ctl01WindowsMenu1SiteMapMenu_2_3M class=" igmn_Island  igmn_Island menu-bar" style="POSITION: relative" submenu="1">
<DIV scrollDiv="1">
<TABLE class=" igmn_Island  igmn_Island menu-bar" style="BORDER-LEFT-WIDTH: 0px; BORDER-RIGHT-WIDTH: 0px; BORDER-BOTTOM-WIDTH: 0px; BORDER-COLLAPSE: collapse; POSITION: relative; BORDER-TOP-WIDTH: 0px" cellSpacing=0 cellPadding=2 border=0>
<TBODY>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_1 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" >
<TBODY>
<TR>
<TD width=25><IMG src=""></TD>
<TD igtxt="1"><NOBR>工单备注</NOBR> </TD>
<TD width=15></TD></TR></TBODY></TABLE></TD></TR>
<TR igitem="1">
<TD>
<TABLE id=ctl01WindowsMenu1SiteMapMenu_2_3_2 class=" igmn_Leaf ig_Item igmn_Item ig_a0da865d_r2 menu-item-top" cellSpacing=0 cellPadding=2 width="100%" >
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

    function EnterTextBox3() {
        document.all["ctl01_PortalContent_BomAssembly1_WebGroupBox1_txtMaterialID"].value="1"
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
<TD style="WIDTH: 50%" colSpan=2><INPUT onkeypress="EnterTextBox('btnScan')" onfocus=javascript:this.select() id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_txtSn style="BORDER-TOP: #7c7c94 1px solid; BORDER-RIGHT: #7c7c94 1px solid; WIDTH: 90%; BORDER-BOTTOM: #7c7c94 1px solid; TEXT-TRANSFORM: uppercase; BORDER-LEFT: #7c7c94 1px solid; BACKGROUND-COLOR: whitesmoke" name=ctl01$PortalContent$BomAssembly1$WebGroupBox1$txtSn '''

sec2 = '''></TD>
<TD style="WIDTH: 25%"><A id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_lbtnSnReport href="javascript:__doPostBack('ctl01$PortalContent$BomAssembly1$WebGroupBox1$lbtnSnReport','')">序列号报表</A></TD></TR>
<TR id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_TableRow3>
<TD id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_TableCell5 style="WIDTH: 25%"><SPAN id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_lblDisAssemblySN>拆卸序列号：</SPAN></TD>
<TD id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_TableCell6 style="WIDTH: 50%" colSpan=2><INPUT onkeypress="EnterTextBox2('btnDisAssemblySn')" onfocus=javascript:this.select() id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_txtDisassemblySerialNumber style="BORDER-TOP: #7c7c94 1px solid; BORDER-RIGHT: #7c7c94 1px solid; WIDTH: 90%; BORDER-BOTTOM: #7c7c94 1px solid; TEXT-TRANSFORM: uppercase; BORDER-LEFT: #7c7c94 1px solid; BACKGROUND-COLOR: whitesmoke" name=ctl01$PortalContent$BomAssembly1$WebGroupBox1$txtDisassemblySerialNumber></TD>
<TD id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_TableCell7 style="WIDTH: 25%"><SPAN id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_lblDisAssemblySnDescription>(仅针对关键物料拆卸)</SPAN></TD></TR>
<TR>
<TD style="WIDTH: 25%"><SPAN id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_Label3>工单号：</SPAN></TD>
<TD style="WIDTH: 50%" colSpan=2><INPUT disabled id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_txtOrder style="BORDER-TOP: #7c7c94 1px solid; BORDER-RIGHT: #7c7c94 1px solid; WIDTH: 90%; BORDER-BOTTOM: #7c7c94 1px solid; BORDER-LEFT: #7c7c94 1px solid; BACKGROUND-COLOR: whitesmoke" readOnly name=ctl01$PortalContent$BomAssembly1$WebGroupBox1$txtOrder></TD>
<TD style="WIDTH: 25%" vAlign=middle rowSpan=2><SPAN id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_lblCount style="FONT-SIZE: xx-large; FONT-WEIGHT: bold; COLOR: red">'''

sec21 = '''</SPAN> &nbsp; <SPAN id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_Label7>(该工单下序列号在该工艺点的过站数量)</SPAN></TD></TR>
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
<DIV id=ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_header class=ajax__tab_header><SPAN id=ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_CABConfigurableTabPanel1_tab class=ajax__tab_active><SPAN class=ajax__tab_outer><SPAN class=ajax__tab_inner><SPAN id=__tab_ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_CABConfigurableTabPanel1 class=ajax__tab_tab><SPAN id=ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_CABConfigurableTabPanel1_Label8>组装</SPAN> </SPAN></SPAN></SPAN></SPAN></DIV>'''


sec3 = '''
<TR>
<TD style="WIDTH: 40%"><SPAN id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_Label21>组件序列号：</SPAN></TD>
<TD style="WIDTH: 60%" colSpan=2><INPUT onkeypress="EnterTextBox2('btnScan')" onfocus=javascript:this.select() id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_txtSecSn style="BORDER-TOP: #7c7c94 1px solid; BORDER-RIGHT: #7c7c94 1px solid; WIDTH: 90%; BORDER-BOTTOM: #7c7c94 1px solid; TEXT-TRANSFORM: uppercase; BORDER-LEFT: #7c7c94 1px solid; BACKGROUND-COLOR: whitesmoke" name=ctl01$PortalContent$BomAssembly1$WebGroupBox1$txtSecSn></TD>
<TR>
<TD id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_TableCell81 style="WIDTH: 33%"><INPUT onkeypress="EnterTextBox3() id=ctl01_PortalContent_BomAssembly1_WebGroupBox1_btnBuild class=btn style="WIDTH: 90%" type=submit value=组装 name=ctl01$PortalContent$BomAssembly1$WebGroupBox1$btnBuild></TD>
></TD></TR>
'''


sec4 = '''<DIV id=ctl01_PortalContent_BomAssembly1_CABConfigurableTab1_body class=ajax__tab_body>
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
WebForm_AutoFocus('ctl01_PortalContent_BomAssembly1_WebGroupBox1_txtSn');Sys.Application.initialize();
//]]>
</SCRIPT>

</FORM></BODY></HTML>'''

