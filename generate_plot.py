year = "2017"

import sys, os
import ROOT as R

os.environ["ANALYSISHOME"] = "/home/mo/Analysis/HMuMu"
sys.path.append(os.path.join(os.environ["ANALYSISHOME"], "Configuration", "higgs"))

import Samples as S


def plot_variable(variable, logy=True):
    canvas = R.TCanvas("c1", "c1")
    canvas.cd()
    pad1 = R.TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
    pad1.SetBottomMargin(0)
    pad1.Draw()
    canvas.cd()
    pad2 = R.TPad("pad2", "pad2", 0, 0.05, 1, 0.3)
    pad2.Draw()
    pad2.cd()
    pad2.SetTopMargin(0.05)
    pad2.SetBottomMargin(0.2)
    pad2.SetGridy()
    pad1.cd()

    bkgStack = R.THStack("bkgStack", "")
    sigStack = R.THStack("sigStack", "")
    allStack = R.THStack("allStack", "")
    hdata = dataTFile.Get(variable)

    leg = R.TLegend(0.8, 0.6, .95, 1.)
    leg.SetHeader("Samples")
    leg.AddEntry(hdata, "data")

    sigHistos = []
    i = 0
    j = 0
    for v in root_dic:
        histo = v[1]["TFile"].Get(variable)
        if not v[1]["isSignal"]:
            histo.SetLineWidth(0)
            # histo.SetLineColor(R.kBlack)
            histo.SetFillColor(bcColors[(i % len(bcColors))])
            histo.Scale(lumi)
            leg.AddEntry(histo,v[0].split("_")[0])
            bkgStack.Add(histo)
            allStack.Add(histo)
            i += 1

        if v[1]["isSignal"]:
            histo.SetLineColor(sigColors[(j % len(sigColors))])
            histo.Scale(lumi)
            leg.AddEntry(histo,v[0].split("_")[0])
            sigHistos.append(histo)
            sigStack.Add(histo)
            allStack.Add(histo)
            j += 1

    # blind data in 120-130 GeV bins
    if variable == "dimuon_mass":
        for i in range(hdata.GetNbinsX()):
            if hdata.GetBinCenter(i + 1) > 120 and hdata.GetBinCenter(i + 1) < 130:
                hdata.SetBinContent(i + 1, 0)

    hdata.SetMarkerStyle(20)
    hdata.SetMarkerSize(.5)

    if logy:
        pad1.SetLogy()
        bkgStack.SetMinimum(.001)

    bkgStack.SetMaximum(hdata.GetMaximum() * 10)
    hdata.SetStats(R.kFALSE)
    hdata.GetXaxis().SetLabelSize(0)
    bkgStack.Draw("hist")
    for h in sigHistos:
        h.Draw("hist same")
    hdata.Draw("SAME P")
    bkgStack.GetXaxis().SetTitle(variable)
    bkgStack.GetYaxis().SetTitle("# Events")
    leg.Draw()
    # pad1.BuildLegend()
    R.gPad.Modified()

    pad2.cd()
    hratio = hdata.Clone()
    hratio.SetTitle("")
    hratio.GetYaxis().SetTitle("Data / MC")
    hratio.GetXaxis().SetTitle(variable)
    hratio.GetYaxis().SetNdivisions(6, R.kFALSE)
    hratio.GetYaxis().SetTitleSize(10)
    hratio.GetYaxis().SetTitleFont(43)
    hratio.GetYaxis().SetTitleOffset(1.55)
    hratio.GetYaxis().SetLabelFont(43)
    hratio.GetYaxis().SetLabelSize(15)
    hratio.GetXaxis().SetTitleSize(10)
    hratio.GetXaxis().SetTitleFont(43)
    hratio.GetXaxis().SetTitleOffset(4)
    hratio.GetXaxis().SetLabelFont(43)
    hratio.GetXaxis().SetLabelSize(15)
    hratio.Divide(allStack.GetStack().Last())
    hratio.SetStats(R.kFALSE)
    hratio.Draw("E P")
    hratio.SetMaximum(1.6)
    hratio.SetMinimum(0.4)
    hratio.SetMarkerStyle(20)
    hratio.SetMarkerSize(0.5)
    R.gPad.Modified()
    canvas.Draw()
    canvas.SaveAs("plots/" + variable + ".pdf")
    outfile.cd()
    canvas.Write()
    del canvas, pad1, pad2, hratio, bkgStack, sigStack, hdata


if __name__ == "__main__":

    datafile = "/home/mo/Analysis/histoFiles/{}/allData{}.root".format(year,year)
    mc2016 = S.mc_background_2016
    mc2016.update(S.mc_signal_2016)

    mc2017 = S.mc_background_2017
    mc2017.update(S.mc_signal_2017)

    mc2018 = S.mc_background_2018
    mc2018.update(S.mc_signal_2018)

    mc_datasets_dic = {
        "2016": mc2016,
        "2017": mc2017,
        "2018": mc2018
    }

    lumi = {
        "2016": 35545.5,
        "2017": 41859.5,
        "2018": 58877.4
    }

    mc_samples = mc_datasets_dic[year]
    root_dic = []
    
    lumi = lumi[year]

    bcColors = [40, 30, 41, 42, 43, 35, 46, 47, 38, 28, 29]
    sigColors = [2, 3, 4, 6, 8, 9]

    for file in os.listdir("/home/mo/Analysis/histoFiles/{}/".format(year)):
        if file.endswith(".root") and not file.startswith("all"):
            nickname = file.replace(".root", "")
            dic = {}
            dic["fullname"] = file
            for k, v in mc_samples.items():
                if nickname in k:
                    dic["isSignal"] = v.isSignal
            f = R.TFile.Open("/home/mo/Analysis/histoFiles/{}/".format(year)+file)
            dic["TFile"] = f
            root_dic.append((nickname, dic))

    # root_dic_sorted = sorted(root_dic, key=lambda el: el[1]['wEvents'])
    # root_dic_sorted = root_dic
    dataTFile = R.TFile.Open(datafile)
    variables = [
        'dimuon_mass'
    ]

    # for jetMass in range(0,510,10):
    #     histo_name = 'dimuon_mass_jet_{}'.format(jetMass)
    #     variables.append(histo_name)

    outfile = R.TFile.Open("plots/plots.root", "UPDATE")
    for variable in variables:
        # print(variable)
        plot_variable(variable)
    outfile.Close()

    # plot_muon_corr()
