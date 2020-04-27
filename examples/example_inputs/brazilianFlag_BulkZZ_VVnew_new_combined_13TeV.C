void brazilianFlag_BulkZZ_VVnew_new_combined_13TeV()
{
//=========Macro generated from canvas: c1/c1
//=========  (Fri Oct 13 17:10:04 2017) by ROOT version6.02/05
   TCanvas *c1 = new TCanvas("c1", "c1",66,78,800,600);
   gStyle->SetOptFit(1);
   gStyle->SetOptStat(0);
   gStyle->SetOptTitle(0);
   c1->SetHighLightColor(2);
   c1->Range(0.7857143,-4.905614,4.238095,2.641169);
   c1->SetFillColor(0);
   c1->SetBorderMode(0);
   c1->SetBorderSize(2);
   c1->SetLogy();
   c1->SetLeftMargin(0.12);
   c1->SetRightMargin(0.04);
   c1->SetTopMargin(0.08);
   c1->SetBottomMargin(0.12);
   c1->SetFrameFillStyle(0);
   c1->SetFrameBorderMode(0);
   c1->SetFrameFillStyle(0);
   c1->SetFrameBorderMode(0);

   TH1F *hframe1 = new TH1F("hframe1","",1000,1.2,4.1);
   hframe1->SetMinimum(0.0001);
   hframe1->SetMaximum(109);
   hframe1->SetDirectory(0);
   hframe1->SetStats(0);
   hframe1->SetLineStyle(0);
   hframe1->SetMarkerStyle(20);
   hframe1->GetXaxis()->SetTitle("M_{G_{Bulk}} (TeV)");
   hframe1->GetXaxis()->SetNdivisions(508);
   hframe1->GetXaxis()->SetLabelFont(42);
   hframe1->GetXaxis()->SetLabelOffset(0.007);
   hframe1->GetXaxis()->SetTitleSize(0.05);
   hframe1->GetXaxis()->SetTitleOffset(1.05);
   hframe1->GetXaxis()->SetTitleFont(42);
   hframe1->GetYaxis()->SetTitle("#sigma #times #bf{#it{#Beta}}(G_{Bulk} #rightarrow ZZ) (pb)");
   hframe1->GetYaxis()->SetLabelFont(42);
   hframe1->GetYaxis()->SetLabelOffset(0.007);
   hframe1->GetYaxis()->SetTitleSize(0.05);
   hframe1->GetYaxis()->SetTitleOffset(1.15);
   hframe1->GetYaxis()->SetTitleFont(42);
   hframe1->GetZaxis()->SetLabelFont(42);
   hframe1->GetZaxis()->SetLabelOffset(0.007);
   hframe1->GetZaxis()->SetLabelSize(0.05);
   hframe1->GetZaxis()->SetTitleSize(0.06);
   hframe1->GetZaxis()->SetTitleFont(42);
   hframe1->Draw(" ");

   Double_t Graph0_fx1[60] = {
   1.2,
   1.3,
   1.4,
   1.5,
   1.6,
   1.7,
   1.8,
   1.9,
   2,
   2.1,
   2.2,
   2.3,
   2.4,
   2.5,
   2.6,
   2.7,
   2.8,
   2.9,
   3,
   3.1,
   3.2,
   3.3,
   3.4,
   3.5,
   3.6,
   3.7,
   3.8,
   3.9,
   4,
   4.1,
   4.1,
   4,
   3.9,
   3.8,
   3.7,
   3.6,
   3.5,
   3.4,
   3.3,
   3.2,
   3.1,
   3,
   2.9,
   2.8,
   2.7,
   2.6,
   2.5,
   2.4,
   2.3,
   2.2,
   2.1,
   2,
   1.9,
   1.8,
   1.7,
   1.6,
   1.5,
   1.4,
   1.3,
   1.2};
   Double_t Graph0_fy1[60] = {
   0.01595315,
   0.01137211,
   0.008485666,
   0.006614575,
   0.005102327,
   0.004022337,
   0.003202503,
   0.002579359,
   0.002131173,
   0.001797356,
   0.0015182,
   0.001345438,
   0.001190896,
   0.001064013,
   0.000977376,
   0.0008746895,
   0.0008029064,
   0.000722928,
   0.0006655113,
   0.0006069727,
   0.0005659956,
   0.0005199696,
   0.0004851391,
   0.0004552844,
   0.0004135268,
   0.0003896235,
   0.0003705009,
   0.0003561589,
   0.0003370363,
   0.0003226943,
   0.00255538,
   0.002668953,
   0.002820267,
   0.002933835,
   0.003085068,
   0.003274269,
   0.003463533,
   0.003690498,
   0.003955294,
   0.004182393,
   0.004454959,
   0.004760982,
   0.005135107,
   0.005518466,
   0.00592637,
   0.00645113,
   0.006971318,
   0.007641557,
   0.008419919,
   0.00937533,
   0.01076798,
   0.01255619,
   0.01494493,
   0.0181399,
   0.02226404,
   0.02746336,
   0.03493462,
   0.04399361,
   0.05763384,
   0.08203879};
   TGraph *graph = new TGraph(60,Graph0_fx1,Graph0_fy1);
   graph->SetName("Graph0");
   graph->SetTitle("Graph");

   Int_t ci;      // for color index setting
   TColor *color; // for color definition with alpha
   ci = TColor::GetColor("#ffcc00");
   graph->SetFillColor(ci);

   ci = TColor::GetColor("#ffcc00");
   graph->SetLineColor(ci);
   graph->SetMarkerStyle(20);

   TH1F *Graph_Graph1 = new TH1F("Graph_Graph1","Graph",100,0.91,4.39);
   Graph_Graph1->SetMinimum(0.0002904249);
   Graph_Graph1->SetMaximum(0.0902104);
   Graph_Graph1->SetDirectory(0);
   Graph_Graph1->SetStats(0);
   Graph_Graph1->SetLineStyle(0);
   Graph_Graph1->SetMarkerStyle(20);
   Graph_Graph1->GetXaxis()->SetLabelFont(42);
   Graph_Graph1->GetXaxis()->SetLabelOffset(0.007);
   Graph_Graph1->GetXaxis()->SetLabelSize(0.05);
   Graph_Graph1->GetXaxis()->SetTitleSize(0.06);
   Graph_Graph1->GetXaxis()->SetTitleOffset(0.9);
   Graph_Graph1->GetXaxis()->SetTitleFont(42);
   Graph_Graph1->GetYaxis()->SetLabelFont(42);
   Graph_Graph1->GetYaxis()->SetLabelOffset(0.007);
   Graph_Graph1->GetYaxis()->SetLabelSize(0.05);
   Graph_Graph1->GetYaxis()->SetTitleSize(0.06);
   Graph_Graph1->GetYaxis()->SetTitleOffset(1.25);
   Graph_Graph1->GetYaxis()->SetTitleFont(42);
   Graph_Graph1->GetZaxis()->SetLabelFont(42);
   Graph_Graph1->GetZaxis()->SetLabelOffset(0.007);
   Graph_Graph1->GetZaxis()->SetLabelSize(0.05);
   Graph_Graph1->GetZaxis()->SetTitleSize(0.06);
   Graph_Graph1->GetZaxis()->SetTitleFont(42);
   graph->SetHistogram(Graph_Graph1);

   graph->Draw("f");

   Double_t Graph1_fx2[60] = {
   1.2,
   1.3,
   1.4,
   1.5,
   1.6,
   1.7,
   1.8,
   1.9,
   2,
   2.1,
   2.2,
   2.3,
   2.4,
   2.5,
   2.6,
   2.7,
   2.8,
   2.9,
   3,
   3.1,
   3.2,
   3.3,
   3.4,
   3.5,
   3.6,
   3.7,
   3.8,
   3.9,
   4,
   4.1,
   4.1,
   4,
   3.9,
   3.8,
   3.7,
   3.6,
   3.5,
   3.4,
   3.3,
   3.2,
   3.1,
   3,
   2.9,
   2.8,
   2.7,
   2.6,
   2.5,
   2.4,
   2.3,
   2.2,
   2.1,
   2,
   1.9,
   1.8,
   1.7,
   1.6,
   1.5,
   1.4,
   1.3,
   1.2};
   Double_t Graph1_fy2[60] = {
   0.02217097,
   0.01576992,
   0.01184516,
   0.009217427,
   0.007141818,
   0.005655557,
   0.00452342,
   0.003660109,
   0.003028332,
   0.00255747,
   0.00217565,
   0.001932701,
   0.001719004,
   0.00154723,
   0.001406285,
   0.00127097,
   0.001166666,
   0.001061114,
   0.000976838,
   0.0009002073,
   0.0008394338,
   0.0007836981,
   0.0007312015,
   0.0006862045,
   0.0006374985,
   0.0005957413,
   0.0005665025,
   0.0005445734,
   0.0005153345,
   0.0004934054,
   0.00154857,
   0.001617395,
   0.001694328,
   0.001762556,
   0.001829185,
   0.001932793,
   0.002044515,
   0.002159168,
   0.002293378,
   0.002425055,
   0.002577029,
   0.002772753,
   0.002984393,
   0.003223677,
   0.003511886,
   0.003817528,
   0.004155923,
   0.004589493,
   0.005091001,
   0.005665162,
   0.006556213,
   0.007707147,
   0.009248577,
   0.01127572,
   0.01390637,
   0.01732098,
   0.02210318,
   0.02798274,
   0.03686041,
   0.0521819};
   graph = new TGraph(60,Graph1_fx2,Graph1_fy2);
   graph->SetName("Graph1");
   graph->SetTitle("Graph");

   ci = TColor::GetColor("#00cc00");
   graph->SetFillColor(ci);

   ci = TColor::GetColor("#00cc00");
   graph->SetLineColor(ci);
   graph->SetMarkerStyle(20);

   TH1F *Graph_Graph2 = new TH1F("Graph_Graph2","Graph",100,0.91,4.39);
   Graph_Graph2->SetMinimum(0.0004440649);
   Graph_Graph2->SetMaximum(0.05735075);
   Graph_Graph2->SetDirectory(0);
   Graph_Graph2->SetStats(0);
   Graph_Graph2->SetLineStyle(0);
   Graph_Graph2->SetMarkerStyle(20);
   Graph_Graph2->GetXaxis()->SetLabelFont(42);
   Graph_Graph2->GetXaxis()->SetLabelOffset(0.007);
   Graph_Graph2->GetXaxis()->SetLabelSize(0.05);
   Graph_Graph2->GetXaxis()->SetTitleSize(0.06);
   Graph_Graph2->GetXaxis()->SetTitleOffset(0.9);
   Graph_Graph2->GetXaxis()->SetTitleFont(42);
   Graph_Graph2->GetYaxis()->SetLabelFont(42);
   Graph_Graph2->GetYaxis()->SetLabelOffset(0.007);
   Graph_Graph2->GetYaxis()->SetLabelSize(0.05);
   Graph_Graph2->GetYaxis()->SetTitleSize(0.06);
   Graph_Graph2->GetYaxis()->SetTitleOffset(1.25);
   Graph_Graph2->GetYaxis()->SetTitleFont(42);
   Graph_Graph2->GetZaxis()->SetLabelFont(42);
   Graph_Graph2->GetZaxis()->SetLabelOffset(0.007);
   Graph_Graph2->GetZaxis()->SetLabelSize(0.05);
   Graph_Graph2->GetZaxis()->SetTitleSize(0.06);
   Graph_Graph2->GetZaxis()->SetTitleFont(42);
   graph->SetHistogram(Graph_Graph2);

   graph->Draw("f");

   Double_t Graph2_fx1001[30] = {
   1.2,
   1.3,
   1.4,
   1.5,
   1.6,
   1.7,
   1.8,
   1.9,
   2,
   2.1,
   2.2,
   2.3,
   2.4,
   2.5,
   2.6,
   2.7,
   2.8,
   2.9,
   3,
   3.1,
   3.2,
   3.3,
   3.4,
   3.5,
   3.6,
   3.7,
   3.8,
   3.9,
   4,
   4.1};
   Double_t Graph2_fy1001[30] = {
   0.03306888,
   0.0234779,
   0.01773331,
   0.01393688,
   0.0108398,
   0.00861689,
   0.006918488,
   0.005619711,
   0.004683092,
   0.003983751,
   0.003409291,
   0.003034644,
   0.002709949,
   0.00245394,
   0.002254128,
   0.002054317,
   0.001885725,
   0.001729622,
   0.001592251,
   0.001479857,
   0.001379951,
   0.001305022,
   0.001217604,
   0.001142675,
   0.001080233,
   0.001017792,
   0.0009678391,
   0.0009303744,
   0.0008804214,
   0.0008429566};
   Double_t Graph2_fex1001[30] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   Double_t Graph2_fey1001[30] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   TGraphErrors *gre = new TGraphErrors(30,Graph2_fx1001,Graph2_fy1001,Graph2_fex1001,Graph2_fey1001);
   gre->SetName("Graph2");
   gre->SetTitle("Graph");
   gre->SetFillColor(1);
   gre->SetLineStyle(3);
   gre->SetLineWidth(4);
   gre->SetMarkerStyle(20);

   TH1F *Graph_Graph1001 = new TH1F("Graph_Graph1001","Graph",100,0.91,4.39);
   Graph_Graph1001->SetMinimum(0.000758661);
   Graph_Graph1001->SetMaximum(0.03629147);
   Graph_Graph1001->SetDirectory(0);
   Graph_Graph1001->SetStats(0);
   Graph_Graph1001->SetLineStyle(0);
   Graph_Graph1001->SetMarkerStyle(20);
   Graph_Graph1001->GetXaxis()->SetLabelFont(42);
   Graph_Graph1001->GetXaxis()->SetLabelOffset(0.007);
   Graph_Graph1001->GetXaxis()->SetLabelSize(0.05);
   Graph_Graph1001->GetXaxis()->SetTitleSize(0.06);
   Graph_Graph1001->GetXaxis()->SetTitleOffset(0.9);
   Graph_Graph1001->GetXaxis()->SetTitleFont(42);
   Graph_Graph1001->GetYaxis()->SetLabelFont(42);
   Graph_Graph1001->GetYaxis()->SetLabelOffset(0.007);
   Graph_Graph1001->GetYaxis()->SetLabelSize(0.05);
   Graph_Graph1001->GetYaxis()->SetTitleSize(0.06);
   Graph_Graph1001->GetYaxis()->SetTitleOffset(1.25);
   Graph_Graph1001->GetYaxis()->SetTitleFont(42);
   Graph_Graph1001->GetZaxis()->SetLabelFont(42);
   Graph_Graph1001->GetZaxis()->SetLabelOffset(0.007);
   Graph_Graph1001->GetZaxis()->SetLabelSize(0.05);
   Graph_Graph1001->GetZaxis()->SetTitleSize(0.06);
   Graph_Graph1001->GetZaxis()->SetTitleFont(42);
   gre->SetHistogram(Graph_Graph1001);

   gre->Draw("l");

   Double_t Graph3_fx1002[30] = {
   1.2,
   1.3,
   1.4,
   1.5,
   1.6,
   1.7,
   1.8,
   1.9,
   2,
   2.1,
   2.2,
   2.3,
   2.4,
   2.5,
   2.6,
   2.7,
   2.8,
   2.9,
   3,
   3.1,
   3.2,
   3.3,
   3.4,
   3.5,
   3.6,
   3.7,
   3.8,
   3.9,
   4,
   4.1};
   Double_t Graph3_fy1002[30] = {
   0.03598755,
   0.01610116,
   0.02320307,
   0.01525207,
   0.005968025,
   0.008148118,
   0.008378009,
   0.006453676,
   0.005740356,
   0.005050603,
   0.005455484,
   0.0049174,
   0.003183152,
   0.002217362,
   0.002256415,
   0.002605496,
   0.002598886,
   0.002560049,
   0.002647637,
   0.002457457,
   0.002286259,
   0.00202766,
   0.001160274,
   0.0007028884,
   0.0005824113,
   0.0005595336,
   0.0005714641,
   0.0005831253,
   0.0005912939,
   0.0005886642};
   Double_t Graph3_fex1002[30] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   Double_t Graph3_fey1002[30] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   gre = new TGraphErrors(30,Graph3_fx1002,Graph3_fy1002,Graph3_fex1002,Graph3_fey1002);
   gre->SetName("Graph3");
   gre->SetTitle("Graph");
   gre->SetFillColor(1);
   gre->SetLineWidth(2);
   gre->SetMarkerStyle(8);
   gre->SetMarkerSize(0.8);

   TH1F *Graph_Graph1002 = new TH1F("Graph_Graph1002","Graph",100,0.91,4.39);
   Graph_Graph1002->SetMinimum(0.0005035803);
   Graph_Graph1002->SetMaximum(0.03953035);
   Graph_Graph1002->SetDirectory(0);
   Graph_Graph1002->SetStats(0);
   Graph_Graph1002->SetLineStyle(0);
   Graph_Graph1002->SetMarkerStyle(20);
   Graph_Graph1002->GetXaxis()->SetLabelFont(42);
   Graph_Graph1002->GetXaxis()->SetLabelOffset(0.007);
   Graph_Graph1002->GetXaxis()->SetLabelSize(0.05);
   Graph_Graph1002->GetXaxis()->SetTitleSize(0.06);
   Graph_Graph1002->GetXaxis()->SetTitleOffset(0.9);
   Graph_Graph1002->GetXaxis()->SetTitleFont(42);
   Graph_Graph1002->GetYaxis()->SetLabelFont(42);
   Graph_Graph1002->GetYaxis()->SetLabelOffset(0.007);
   Graph_Graph1002->GetYaxis()->SetLabelSize(0.05);
   Graph_Graph1002->GetYaxis()->SetTitleSize(0.06);
   Graph_Graph1002->GetYaxis()->SetTitleOffset(1.25);
   Graph_Graph1002->GetYaxis()->SetTitleFont(42);
   Graph_Graph1002->GetZaxis()->SetLabelFont(42);
   Graph_Graph1002->GetZaxis()->SetLabelOffset(0.007);
   Graph_Graph1002->GetZaxis()->SetLabelSize(0.05);
   Graph_Graph1002->GetZaxis()->SetTitleSize(0.06);
   Graph_Graph1002->GetZaxis()->SetTitleFont(42);
   gre->SetHistogram(Graph_Graph1002);

   gre->Draw("lp");

   Double_t BulkZZ_gtheory_fx1003[11] = {
   1,
   1.2,
   1.4,
   1.6,
   1.8,
   2,
   2.5,
   3,
   3.5,
   4,
   4.5};
   Double_t BulkZZ_gtheory_fy1003[11] = {
   0.01024985,
   0.00341978,
   0.00130687,
   0.0005741872,
   0.0002441465,
   0.0001197594,
   2.242854e-05,
   4.91243e-06,
   2.098791e-06,
   1.219122e-06,
   1.044836e-06};
   Double_t BulkZZ_gtheory_fex1003[11] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   Double_t BulkZZ_gtheory_fey1003[11] = {
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0,
   0};
   gre = new TGraphErrors(11,BulkZZ_gtheory_fx1003,BulkZZ_gtheory_fy1003,BulkZZ_gtheory_fex1003,BulkZZ_gtheory_fey1003);
   gre->SetName("BulkZZ_gtheory");
   gre->SetTitle("Graph");
   gre->SetFillColor(1);

   ci = TColor::GetColor("#ff0000");
   gre->SetLineColor(ci);
   gre->SetLineWidth(3);

   TH1F *Graph_BulkZZ_gtheory1003 = new TH1F("Graph_BulkZZ_gtheory1003","Graph",100,0.65,4.85);
   Graph_BulkZZ_gtheory1003->SetMinimum(9.403527e-07);
   Graph_BulkZZ_gtheory1003->SetMaximum(0.01127473);
   Graph_BulkZZ_gtheory1003->SetDirectory(0);
   Graph_BulkZZ_gtheory1003->SetStats(0);
   Graph_BulkZZ_gtheory1003->SetLineStyle(0);
   Graph_BulkZZ_gtheory1003->SetMarkerStyle(20);
   Graph_BulkZZ_gtheory1003->GetXaxis()->SetLabelFont(42);
   Graph_BulkZZ_gtheory1003->GetXaxis()->SetLabelOffset(0.007);
   Graph_BulkZZ_gtheory1003->GetXaxis()->SetLabelSize(0.05);
   Graph_BulkZZ_gtheory1003->GetXaxis()->SetTitleSize(0.06);
   Graph_BulkZZ_gtheory1003->GetXaxis()->SetTitleOffset(0.9);
   Graph_BulkZZ_gtheory1003->GetXaxis()->SetTitleFont(42);
   Graph_BulkZZ_gtheory1003->GetYaxis()->SetLabelFont(42);
   Graph_BulkZZ_gtheory1003->GetYaxis()->SetLabelOffset(0.007);
   Graph_BulkZZ_gtheory1003->GetYaxis()->SetLabelSize(0.05);
   Graph_BulkZZ_gtheory1003->GetYaxis()->SetTitleSize(0.06);
   Graph_BulkZZ_gtheory1003->GetYaxis()->SetTitleOffset(1.25);
   Graph_BulkZZ_gtheory1003->GetYaxis()->SetTitleFont(42);
   Graph_BulkZZ_gtheory1003->GetZaxis()->SetLabelFont(42);
   Graph_BulkZZ_gtheory1003->GetZaxis()->SetLabelOffset(0.007);
   Graph_BulkZZ_gtheory1003->GetZaxis()->SetLabelSize(0.05);
   Graph_BulkZZ_gtheory1003->GetZaxis()->SetTitleSize(0.06);
   Graph_BulkZZ_gtheory1003->GetZaxis()->SetTitleFont(42);
   gre->SetHistogram(Graph_BulkZZ_gtheory1003);

   gre->Draw("l");

   Double_t BulkZZ_grshade_fx3[22] = {
   1,
   1.2,
   1.4,
   1.6,
   1.8,
   2,
   2.5,
   3,
   3.5,
   4,
   4.5,
   4.5,
   4,
   3.5,
   3,
   2.5,
   2,
   1.8,
   1.6,
   1.4,
   1.2,
   1};
   Double_t BulkZZ_grshade_fy3[22] = {
   0.0134007,
   0.004611356,
   0.001811763,
   0.0008217326,
   0.0003600711,
   0.0001818294,
   3.647573e-05,
   8.680007e-06,
   4.007235e-06,
   2.568563e-06,
   2.408994e-06,
   9.808328e-08,
   2.553502e-07,
   6.904563e-07,
   2.048e-06,
   1.139506e-05,
   6.948064e-05,
   0.000148981,
   0.0003680936,
   0.0008800111,
   0.002397691,
   0.007501346};
   graph = new TGraph(22,BulkZZ_grshade_fx3,BulkZZ_grshade_fy3);
   graph->SetName("BulkZZ_grshade");
   graph->SetTitle("Graph");

   ci = TColor::GetColor("#ff0000");
   graph->SetFillColor(ci);
   graph->SetFillStyle(3013);
   graph->SetLineColor(0);

   TH1F *Graph_BulkZZ_grshade3 = new TH1F("Graph_BulkZZ_grshade3","Graph",100,0.65,4.85);
   Graph_BulkZZ_grshade3->SetMinimum(8.827495e-08);
   Graph_BulkZZ_grshade3->SetMaximum(0.01474076);
   Graph_BulkZZ_grshade3->SetDirectory(0);
   Graph_BulkZZ_grshade3->SetStats(0);
   Graph_BulkZZ_grshade3->SetLineStyle(0);
   Graph_BulkZZ_grshade3->SetMarkerStyle(20);
   Graph_BulkZZ_grshade3->GetXaxis()->SetLabelFont(42);
   Graph_BulkZZ_grshade3->GetXaxis()->SetLabelOffset(0.007);
   Graph_BulkZZ_grshade3->GetXaxis()->SetLabelSize(0.05);
   Graph_BulkZZ_grshade3->GetXaxis()->SetTitleSize(0.06);
   Graph_BulkZZ_grshade3->GetXaxis()->SetTitleOffset(0.9);
   Graph_BulkZZ_grshade3->GetXaxis()->SetTitleFont(42);
   Graph_BulkZZ_grshade3->GetYaxis()->SetLabelFont(42);
   Graph_BulkZZ_grshade3->GetYaxis()->SetLabelOffset(0.007);
   Graph_BulkZZ_grshade3->GetYaxis()->SetLabelSize(0.05);
   Graph_BulkZZ_grshade3->GetYaxis()->SetTitleSize(0.06);
   Graph_BulkZZ_grshade3->GetYaxis()->SetTitleOffset(1.25);
   Graph_BulkZZ_grshade3->GetYaxis()->SetTitleFont(42);
   Graph_BulkZZ_grshade3->GetZaxis()->SetLabelFont(42);
   Graph_BulkZZ_grshade3->GetZaxis()->SetLabelOffset(0.007);
   Graph_BulkZZ_grshade3->GetZaxis()->SetLabelSize(0.05);
   Graph_BulkZZ_grshade3->GetZaxis()->SetTitleSize(0.06);
   Graph_BulkZZ_grshade3->GetZaxis()->SetTitleFont(42);
   graph->SetHistogram(Graph_BulkZZ_grshade3);

   graph->Draw("f");

   TPaveText *pt = new TPaveText(0.52,0.2,0.8,0.9,"brNDC");
   pt->SetBorderSize(0);
   pt->SetFillColor(0);
   pt->SetFillStyle(0);
   pt->SetLineColor(0);
   pt->SetTextAlign(12);
   pt->SetTextFont(42);
   pt->SetTextSize(0.035);
   TText *AText = pt->AddText("Narrow width approximation");
   pt->Draw();
   TLatex *tex = new TLatex(0.96,0.936,"35.9 fb^{-1} (13 TeV)");
tex->SetNDC();
   tex->SetTextAlign(31);
   tex->SetTextFont(42);
   tex->SetTextSize(0.048);
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.1578,0.892,"CMS");
tex->SetNDC();
   tex->SetTextAlign(13);
   tex->SetTextFont(61);
   tex->SetTextSize(0.06);
   tex->SetLineWidth(2);
   tex->Draw();
      tex = new TLatex(0.1578,0.82,"");
tex->SetNDC();
   tex->SetTextAlign(13);
   tex->SetTextFont(52);
   tex->SetTextSize(0.0456);
   tex->SetLineWidth(2);
   tex->Draw();

   TH1F *hframe_copy2 = new TH1F("hframe_copy2","",1000,1.2,4.1);
   hframe_copy2->SetMinimum(0.0001);
   hframe_copy2->SetMaximum(109);
   hframe_copy2->SetDirectory(0);
   hframe_copy2->SetStats(0);
   hframe_copy2->SetLineStyle(0);
   hframe_copy2->SetMarkerStyle(20);
   hframe_copy2->GetXaxis()->SetTitle("M_{G_{Bulk}} (TeV)");
   hframe_copy2->GetXaxis()->SetNdivisions(508);
   hframe_copy2->GetXaxis()->SetLabelFont(42);
   hframe_copy2->GetXaxis()->SetLabelOffset(0.007);
   hframe_copy2->GetXaxis()->SetTitleSize(0.05);
   hframe_copy2->GetXaxis()->SetTitleOffset(1.05);
   hframe_copy2->GetXaxis()->SetTitleFont(42);
   hframe_copy2->GetYaxis()->SetTitle("#sigma #times #bf{#it{#Beta}}(G_{Bulk} #rightarrow ZZ) (pb)");
   hframe_copy2->GetYaxis()->SetLabelFont(42);
   hframe_copy2->GetYaxis()->SetLabelOffset(0.007);
   hframe_copy2->GetYaxis()->SetTitleSize(0.05);
   hframe_copy2->GetYaxis()->SetTitleOffset(1.15);
   hframe_copy2->GetYaxis()->SetTitleFont(42);
   hframe_copy2->GetZaxis()->SetLabelFont(42);
   hframe_copy2->GetZaxis()->SetLabelOffset(0.007);
   hframe_copy2->GetZaxis()->SetLabelSize(0.05);
   hframe_copy2->GetZaxis()->SetTitleSize(0.06);
   hframe_copy2->GetZaxis()->SetTitleFont(42);
   hframe_copy2->Draw("sameaxis");

   TH1F *hframe_copy3 = new TH1F("hframe_copy3","",1000,1.2,4.1);
   hframe_copy3->SetMinimum(0.0001);
   hframe_copy3->SetMaximum(109);
   hframe_copy3->SetDirectory(0);
   hframe_copy3->SetStats(0);
   hframe_copy3->SetLineStyle(0);
   hframe_copy3->SetMarkerStyle(20);
   hframe_copy3->GetXaxis()->SetTitle("M_{G_{Bulk}} (TeV)");
   hframe_copy3->GetXaxis()->SetNdivisions(508);
   hframe_copy3->GetXaxis()->SetLabelFont(42);
   hframe_copy3->GetXaxis()->SetLabelOffset(0.007);
   hframe_copy3->GetXaxis()->SetTitleSize(0.05);
   hframe_copy3->GetXaxis()->SetTitleOffset(1.05);
   hframe_copy3->GetXaxis()->SetTitleFont(42);
   hframe_copy3->GetYaxis()->SetTitle("#sigma #times #bf{#it{#Beta}}(G_{Bulk} #rightarrow ZZ) (pb)");
   hframe_copy3->GetYaxis()->SetLabelFont(42);
   hframe_copy3->GetYaxis()->SetLabelOffset(0.007);
   hframe_copy3->GetYaxis()->SetTitleSize(0.05);
   hframe_copy3->GetYaxis()->SetTitleOffset(1.15);
   hframe_copy3->GetYaxis()->SetTitleFont(42);
   hframe_copy3->GetZaxis()->SetLabelFont(42);
   hframe_copy3->GetZaxis()->SetLabelOffset(0.007);
   hframe_copy3->GetZaxis()->SetLabelSize(0.05);
   hframe_copy3->GetZaxis()->SetTitleSize(0.06);
   hframe_copy3->GetZaxis()->SetTitleFont(42);
   hframe_copy3->Draw("sameaxig");

   TLegend *leg = new TLegend(0.52,0.6002591,0.806734,0.9011917,NULL,"brNDC");
   leg->SetBorderSize(1);
   leg->SetTextFont(62);
   leg->SetTextSize(0.038);
   leg->SetLineColor(0);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(1001);
   TLegendEntry *entry=leg->AddEntry("Graph3","Observed","Lp");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(2);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(8);
   entry->SetMarkerSize(0.8);
   entry->SetTextFont(62);
   entry=leg->AddEntry("Graph1","Expected #pm 1 std. deviation","f");

   ci = TColor::GetColor("#00cc00");
   entry->SetFillColor(ci);
   entry->SetFillStyle(1001);

   ci = TColor::GetColor("#00cc00");
   entry->SetLineColor(ci);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(62);
   entry=leg->AddEntry("Graph0","Expected #pm 2 std. deviation","f");

   ci = TColor::GetColor("#ffcc00");
   entry->SetFillColor(ci);
   entry->SetFillStyle(1001);

   ci = TColor::GetColor("#ffcc00");
   entry->SetLineColor(ci);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(62);
   entry=leg->AddEntry("BulkZZ_gtheory","#sigma_{TH}#times#bf{#it{#Beta}}(G_{Bulk}#rightarrowZZ) #tilde{k}=0.5","L");

   ci = TColor::GetColor("#ff0000");
   entry->SetLineColor(ci);
   entry->SetLineStyle(1);
   entry->SetLineWidth(3);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(62);
   leg->Draw();

   leg = new TLegend(0.52,0.6002591,0.8046734,0.9011917,NULL,"brNDC");
   leg->SetTextFont(62);
   leg->SetTextSize(0.038);
   leg->SetLineColor(0);
   leg->SetLineStyle(1);
   leg->SetLineWidth(1);
   leg->SetFillColor(0);
   leg->SetFillStyle(0);
   entry=leg->AddEntry("Graph3"," ","");
   entry->SetLineColor(1);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(62);
   entry=leg->AddEntry("Graph2"," ","L");
   entry->SetLineColor(1);
   entry->SetLineStyle(3);
   entry->SetLineWidth(4);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(62);
   entry=leg->AddEntry("Graph2"," ","L");
   entry->SetLineColor(1);
   entry->SetLineStyle(3);
   entry->SetLineWidth(4);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(62);
   entry=leg->AddEntry("BulkZZ_grshade"," ","F");

   ci = TColor::GetColor("#ff0000");
   entry->SetFillColor(ci);
   entry->SetFillStyle(3013);
   entry->SetLineStyle(1);
   entry->SetLineWidth(1);
   entry->SetMarkerColor(1);
   entry->SetMarkerStyle(21);
   entry->SetMarkerSize(1);
   entry->SetTextFont(62);
   leg->Draw();
   c1->Modified();
   c1->cd();
   c1->SetSelected(c1);
}
