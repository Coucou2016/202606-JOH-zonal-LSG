# Tan et al. (2025) Hydrology and Earth System Sciences

- **DOI:** https://doi.org/10.5194/hess-29-3833-2025
- **Local PDF:** `paper/refs/pdf/tan2025_hess_regionalized_lsg.pdf`
- **Access:** full text obtained (Copernicus publisher OA PDF (CC BY))
- **Conversion tool:** PyMuPDF (`fitz`) via `paper/refs/_pdf_to_md.py`
- **Pages:** 20

---

## Extracted full text (OCR-free PDF text layer)

### Page 1

Hydrol. Earth Syst. Sci., 29, 3833–3852, 2025
https://doi.org/10.5194/hess-29-3833-2025
© Author(s) 2025. This work is distributed under
the Creative Commons Attribution 4.0 License.

An efﬁcient hybrid downscaling framework to estimate
high-resolution river hydrodynamics

Zeli Tan1, Donghui Xu1, Sourav Taraphdar1, Jiangqin Ma2, Gautam Bisht1, and L. Ruby Leung1

1Paciﬁc Northwest National Laboratory, Richland, WA 99352, USA
2College of Engineering, Georgia Institute of Technology, Atlanta, GA 30332, USA

Correspondence: Zeli Tan (zeli.tan@pnnl.gov)

Received: 4 December 2024 – Discussion started: 3 February 2025
Revised: 1 May 2025 – Accepted: 5 June 2025 – Published: 18 August 2025


#### Abstract. Flow depth and velocity are the most important

hydrodynamic variables that govern various river functions,
including water resources, navigation, sediment transport,
and biogeochemical cycling. Existing high-resolution ﬂow
depth simulations rely on either computationally expensive
river hydrodynamic models (RHMs) or data-driven models
with formidable training costs, whereas data-driven model-
ing of ﬂow velocity has rarely been explored. Here, using
the hybrid Low-ﬁdelity, Spatial analysis, and Gaussian pro-
cess learning (LSG) model, we developed a downscaling ap-
proach to construct high-resolution ﬂow depth and velocity
from a two-dimensional (2-D) RHM simulation at coarse res-
olution. The LSG models were trained and tested in an urban
watershed in Houston using two different hurricane-driven
ﬂood events. The high-resolution (as ﬁne as 30 m resolution)
and low-resolution (mostly 1000 m resolution) meshes in-
clude 664 724 and 14 536 grid cells, respectively. The results
showed that through downscaling, the simulation errors were
reduced to less than one-fourth and one-third of the errors
of the low-resolution 2-D RHM for ﬂow depth and veloc-
ity, respectively. Our analysis further revealed that the dom-
inant uncertainty sources of the downscaled hydrodynamics
are different, with ﬂow velocity dominated by the dimension-
ality reduction error, which we reduced by using a regional-
ized training procedure. The downscaling approach achieves
an 84-fold acceleration in computational time compared to
the high-resolution 2-D RHM, making high-ﬁdelity ensem-
ble ﬂood modeling feasible. More importantly, the developed
method provides an opportunity to couple large-scale hydro-
dynamical processes with local physical, chemical, and bio-
logical processes in river models.

1

#### Introduction


Rivers play a crucial role in water resources, navigation,
sediment transport, and biogeochemical cycling (Syvitski
et al., 2005; Oki and Kanae, 2006; Allen and Pavelsky, 2018;
Ibáñez and Peñuelas, 2019; Mao et al., 2019; Regnier et al.,
2022; Feng et al., 2023a; Rocher-Ros et al., 2023). To sustain
these vital services, river ﬂow depth and velocity must re-
main within normal ranges. Extreme ﬂow depths can result in
extensive ﬂuvial ﬂooding (Bates, 2022), whereas prolonged
low ﬂow depths jeopardize the availability of drinking and
irrigation water in many regions worldwide (Gadgil, 1998;
Haddeland et al., 2006). Together, ﬂow depth and velocity
are key drivers of navigation capability, sediment transport,
and biogeochemical processes in rivers (Zhang et al., 2014;
Raymond et al., 2016; Li et al., 2022; Sukhodolov et al.,
2023). Consequently, extreme variations in ﬂow depth and
velocity can lead to waterway blockage, channel aggradation
or degradation, water quality deterioration, and habitat loss.
River ﬂow depth and velocity regimes are dynamic and inﬂu-
enced by climate change and human activities, leading many
rivers to experience extreme ﬂow conditions (Mishra and
Shah, 2018). These conditions exacerbate ﬂooding (Freer
et al., 2011), degrade aquatic ecosystems (Carpenter et al.,
2011; Battin et al., 2023), and diminish water supplies (Oki
and Kanae, 2006). Hence, accurate prediction of river ﬂow
depth and velocity in the context of a changing climate is es-
sential for ensuring the well-being of human society (IPCC,
2021).
Flow depth and velocity are commonly simulated using
river hydrodynamic models (RHMs). Widely used RHMs are
often based on one-dimensional (1-D) or two-dimensional

Published by Copernicus Publications on behalf of the European Geosciences Union.

### Page 2

3834
Z. Tan et al.: An efﬁcient hybrid downscaling framework to estimate high-resolution river hydrodynamics

(2-D) Saint-Venant equations, disregarding vertical varia-
tions due to the signiﬁcant difference between the horizon-
tal and vertical length scales of rivers (Li et al., 2013; Teng
et al., 2017; Bates, 2022; Huang et al., 2022). Considering the
low computational cost and high numerical stability, Earth
system models (ESMs) usually employ 1-D RHMs as the
river component for large-scale and/or ensemble hydrolog-
ical simulations (Li et al., 2013; Feng et al., 2024). How-
ever, they are unsuitable for high-ﬁdelity ﬂood simulations.
This is because 1-D RHMs are solved on upscaled river net-
works rather than actual river reaches (Wu et al., 2011; Liao
et al., 2022) and rely on uncertain parameterizations, such
as the bathtub method for estimating ﬂoodplain inundation
(Luo et al., 2017; Xu et al., 2022). Additionally, by over-
simplifying and/or neglecting momentum transport in river
channels and ﬂoodplains (Luo et al., 2017; Feng et al., 2022),
1-D RHMs lack the capability to simulate ﬁne-scale river
hydrodynamics required for geomorphological and biogeo-
chemical modeling (Hostache et al., 2014; Shabani et al.,
2021). Conversely, 2-D RHMs can solve full river dynam-
ics. When running on high-resolution meshes, they can ac-
curately capture river ﬂow depth and velocity (Razavi et al.,
2012). Therefore, high-resolution 2-D RHMs are often re-
ferred to as high-ﬁdelity (HF) models, whereas both 1-D
RHMs and low-resolution 2-D RHMs are referred to as low-
ﬁdelity (LF) models. However, the signiﬁcant computational
cost of HF RHMs (Teng et al., 2017; Wu et al., 2020; Ivanov
et al., 2021) makes them not viable for real-time model-
ing and ﬂood risk assessments through ensemble modeling,
which requires hundreds or thousands of model realizations
(Wu et al., 2020).

informed neural networks have been developed, embedding
physical laws (e.g., Saint-Venant equations) into their cost
functions to constrain ML solutions. However, the incorpo-
ration of physical laws tends to reduce the training efﬁciency
of ML models (Feng et al., 2023b).

The second approach is to downscale the low-resolution
RHM simulation onto a ﬁnely discretized grid (Wilby and
Dawson, 2013; Feng et al., 2023b). For instance, Bermúdez
et al. (2020) created high-resolution inundation maps by sim-
ply interpolating ﬂow depth computed from an LF RHM onto
a high-resolution digital elevation model (DEM). Recently,
more advanced downscaling methods have been developed
using various ML techniques to reproduce the detailed spatial
and temporal features of high-resolution river hydrodynam-
ics (Carreau and Guinot, 2021). Notably, Fraehr et al. (2022)
developed a novel downscaling method based on the hybrid
Low-ﬁdelity, Spatial analysis, and Gaussian process learning
(LSG) model. This method demonstrated promising accu-
racy in simulating the dynamic behavior of ﬂood inundation,
such as the rising and recession components and hystere-
sis, at the computational cost of a low-resolution 2-D RHM
(Fraehr et al., 2022). Later, Fraehr et al. (2023a) extended the
approach for fast and accurate simulations of not only high-
resolution ﬂood extent but also high-resolution ﬂow depth.
Additionally, the LSG-based downscaling model can sup-
port both structured and unstructured grids, a signiﬁcant ad-
vantage as modern 2-D RHMs increasingly adopt unstruc-
tured grids for ﬁne-scale modeling (Begnudelli and Sanders,
2006; Kim et al., 2012). However, like Fraehr et al. (2022,
2023a), existing research on hydrodynamic model downscal-
ing is mostly ﬂood-prediction-oriented and has thus focused
entirely on ﬂood extent and magnitude, while ignoring ﬂow
velocity. This oversight is problematic from two perspec-
tives. First, it could increase the uncertainty of ﬂood risk sim-
ulations because ﬂood velocity is a critical factor for human
safety risks in ﬂood events (Russo et al., 2013). Moreover,
as discussed earlier, in the context of Earth system model-
ing, without accurate simulations of ﬂow velocity, it is not
possible to realistically predict how river functions respond
to environmental stresses. While Fraehr et al. (2022, 2023a)
only applied the LSG-based downscaling approach for inun-
dation extent and depth, this method should theoretically also
be applicable for ﬂow velocity. This is because the mass and
momentum of river ﬂow are governed by the uniﬁed shal-
low water equations and driven by the same environmental
factors. However, such an application has not yet been ex-
plored.

To achieve accurate and affordable simulations of river hy-
drodynamics, several alternative approaches have been de-
veloped (Razavi et al., 2012). One prominent approach is
the use of data-driven models to emulate the behaviors of
HF RHMs (Ivanov et al., 2021; Tran et al., 2023). With the
rapid advancement of machine learning (ML) techniques,
ML-based emulators have been increasingly employed in hy-
drological sciences, including applications such as model-
ing runoff (Gao et al., 2020), evapotranspiration (Hu et al.,
2021), inundation (Xie et al., 2021), lake–river interactions
(Liang et al., 2018; Huang et al., 2022), reservoir opera-
tions (Zhang et al., 2018; Yang et al., 2019b), streamﬂow (Ha
et al., 2021; Sikorska-Senoner and Quilty, 2021), groundwa-
ter (He et al., 2020; Wunsch et al., 2022), and water qual-
ity (Chen et al., 2020; Saha et al., 2023). These studies have
demonstrated that, once trained under extensive conditions,
the computationally efﬁcient ML models can mimic numer-
ical models. However, general ML-based emulators often
lack the enforcement of physical laws, such as the conser-
vation of mass and momentum (Konapala et al., 2020; Kar-
niadakis et al., 2021), resulting in poor transferability to out-
of-sample conditions in nonstationary systems (Young et al.,
2017; Konapala et al., 2020), such as streamﬂow in a chang-
ing climate. To address this limitation, variants like physics-

In this study, we develop an LSG-based downscaling ap-
proach to achieve accurate simulations of high-resolution
river ﬂow depth and velocity at the computational cost
of a low-resolution 2-D RHM. Compared to Fraehr et al.
(2022, 2023a), the main innovation of our study is to test
and enhance the LSG-based downscaling approach for high-
resolution ﬂow velocity downscaling. This extension of the
LSG-based downscaling approach is expected to greatly

Hydrol. Earth Syst. Sci., 29, 3833–3852, 2025
https://doi.org/10.5194/hess-29-3833-2025

### Page 3

Z. Tan et al.: An efﬁcient hybrid downscaling framework to estimate high-resolution river hydrodynamics
3835

Figure 1. Workﬂow of training the LSG model and using the trained model to predict high-resolution river hydrodynamics.

broaden its usefulness for Earth system modeling. Besides,
we test the effectiveness of the downscaling method in an
urbanized watershed in the Houston area using data from
two different extreme hurricane events. Together with Fraehr
et al. (2022, 2023a), our independent validation in a differ-
ent environment would help examine whether the LSG-based
downscaling approach has broad geographical applicability.
Furthermore, based on this downscaling method, we propose
a new paradigm to couple large-scale hydrodynamical pro-
cesses with local detailed physical, chemical, and biologi-
cal processes in river models. The remainder of this paper
is organized as follows: Sect. 2 describes the downscaling
method and the conﬁgurations of the high-resolution and
low-resolution 2-D RHMs for the study events; Sect. 3 high-
lights the main results; Sect. 4 discusses the implications of
the results, outlines the limitations of our approach, and in-
troduces the new paradigm; and Sect. 5 concludes the paper.

from an HF RHM, and a sparse Gaussian process (GP) emu-
lator model. It uses the LF RHM as a transfer function to cap-
ture the dynamics and spatial correlation of river ﬂow. The
key temporal features of the LF RHM outputs are extracted
through an empirical orthogonal function (EOF) analysis
based on the extracted spatial features from the HF RHM,
thereby allowing the use of a sparse GP model to convert the
LF data to HF data via conversion of the extracted temporal
features. The LSG model can reconstruct high-ﬁdelity river
hydrodynamics for two reasons. First, the accurate spatial
correlations of river hydrodynamics are preserved due to the
use of the key spatial modes from the HF model, which are
assumed not to vary by event. Second, the sparse GP model is
efﬁcient and effective in reconstructing the dynamics of HF
data. In this study, we used the same 2-D shallow water equa-
tions to construct the LF and HF RHMs (described later). The
only difference between them is the spatial resolution, with
the coarse mesh adopted by the LF model reducing the sim-
ulation accuracy. We followed the procedure described by
Fraehr et al. (2022, 2023a) to train and apply LSG models
for river ﬂow depth and velocity downscaling (Fig. 1), with
any deviations from the general procedure speciﬁcally high-
lighted.

2
Materials and methods

2.1
LSG model

For training, we ﬁrst run the HF RHM over the study
domain for a training ﬂood event (Step 1) and derive the
spatial EOF modes and the temporal expansion coefﬁcient
(EC) modes of this HF simulation through the EOF analysis

For the LSG model, the underlying principle is that the dy-
namics of ﬂow depth and velocity can be approximated by a
limited number of temporal and spatial modes due to their
strong spatial pattern controlled by topography. The LSG
model consists of an LF RHM, key spatial modes extracted

https://doi.org/10.5194/hess-29-3833-2025
Hydrol. Earth Syst. Sci., 29, 3833–3852, 2025

### Page 4

3836
Z. Tan et al.: An efﬁcient hybrid downscaling framework to estimate high-resolution river hydrodynamics

Figure 2. Study domain (a), topography (b), high-resolution mesh (c), and coarse-resolution mesh (d) for river hydrodynamics simulations
in the Turning River basin. The river basin boundary and the boundaries of two reservoirs in the basin are highlighted in orange and blue,
respectively, in (a), and the black dots in (b) show the locations of the USGS gauges (Table S1 in the Supplement) along with their gauge
number. The basemap in (a) is extracted from Google Imagery© 2024 TerraMetrics, Map data© 2024. The seemingly thick bold lines in (c)
are dense grid cells for river channels. The seemingly black lines in (d) are dense grid cells for the dams of the two reservoirs, which can
also be seen in (c).

(Step 2) as deﬁned in Eq. (1).

of river channels and nearby ﬂoodplains that are represented
by smaller grid cells in our ﬁne mesh (Fig. 2).

XK


#### DHF = UHF · CHF ≈


k=1UHF(k,:) · CHF(:,k),
(1)

Next, we perform the EOF analysis on the interpolated LF
ﬂow depth and velocity to derive the temporal EC modes
of the LF simulation (Step 5). Using the extracted high-
resolution EOF spatial modes from Step 2, the extracted tem-
poral ECs are deﬁned in Eq. (2).

where DHF is a T × N matrix containing simulated HF ﬂow
depth or velocity (T is the number of time steps in the train-
ing data and N is the number of wet cells) that have been de-
trended (Fraehr et al., 2023a), UHF is a T × N matrix, each
row of which is an EOF spatial map, CHF is a T × T matrix,
each column of which corresponds to an EC temporal func-
tion, and K is the number of signiﬁcant modes determined
by both North’s test (North et al., 1982) and Kaiser’s rule
(Kaiser, 1960).


#### CLF = DLF · U′



#### HF,

(2)

where CLF is a T × T matrix containing the LF ECs, DLF
is a T × N matrix corresponding to the interpolated LF ﬂow
depth or velocity simulations, and U′

For the training phase, we also run the LF RHM for the
training event (Step 3) and interpolate the simulated ﬂow
depth and velocity from the coarse mesh used by the LF
model to the ﬁne mesh used by the HF model (Step 4).
Notably, we improved the nearest-neighbor interpolation
method adopted by Fraehr et al. (2023a) by accounting for
mass conservation. While our improved method still assumes
a homogeneous water level within a coarse grid cell, it en-
sures that the sum of interpolated water volume in ﬁne grid
cells equals the water volume in the coarse grid cell. Ad-
ditionally, we ensure that the interpolation of ﬂow velocity
only occurs at wet grid cells where the water depth is greater
than 3 cm (Fraehr et al., 2023a). Another difference is that
we do not apply area-based weights to DHF before the EOF
analysis, as Fraehr et al. (2023a) recommended. This is be-
cause we are more interested in the ﬂow depth and velocity

HF is the transpose of
UHF. In the ﬁnal step of training, we use the derived LF and
HF temporal ECs to train a sparse GP model (Rasmussen
and Williams, 2006) that can predict the HF ECs from the
LF ECs (Step 6). For ﬂow depth and velocity, the training of
the sparse GP models is performed independently.

For prediction, only the low-cost LF RHM simulations
are needed (Fig. 1). While Steps 7 to 9 essentially replicate
Steps 3 to 5, the difference is that Steps 7 to 9 are applied
to a new LF simulation that is run for an unseen ﬂood event.
After the new LF ECs are retrieved following the EOF analy-
sis in Eq. (1) using the spatial EOF modes derived in Step 2,
they are fed into the trained sparse GP model to predict the
new HF ECs (Step 10). Finally, the predicted HF ECs are
combined with the EOF spatial modes from Step 2 to recon-
struct the HF ﬂow depth and velocity simulations based on

Hydrol. Earth Syst. Sci., 29, 3833–3852, 2025
https://doi.org/10.5194/hess-29-3833-2025

### Page 5

Z. Tan et al.: An efﬁcient hybrid downscaling framework to estimate high-resolution river hydrodynamics
3837

the reverse EOF analysis (Step 11) as deﬁned in Eq. (3).

ing the European Centre for Medium-Range Weather Fore-
casts (ECMWF) Reanalysis version 5 (ERA5) data (Hers-
bach et al., 2020). These features enable SCREAM to capture
ﬁne-scale extreme weather events, accurately resolve coastal
areas and mountainous regions, and properly represent con-
vective clouds, which are major sources of climate model un-
certainty (Sherwood et al., 2014). SCREAM is coupled with
the E3SM Land Model (ELM), while sea surface temperature
and sea ice extent are prescribed based on ERA5.

K
X

[

#### DLSG =


UHF(k,:) · [
CLSG(:,k),
(3)

k=1

where [
DLSG is the predicted high-resolution ﬂow depth or
velocity, and [
CLSG is the predicted HF temporal EC. More
details of the workﬂow can be found in Fraehr et al. (2022,
2023a).
The downscaling error consists of two major components:
the error from dimensionality reduction and the error from
the LSG model. According to Eq. (1), the error from di-
mensionality reduction ERDR can be deﬁned as ERDR =

#### DHF −PK


In the historical simulation, SCREAM is initialized using
ERA5 to simulate Hurricane Harvey (hereafter referred to as
the SCREAM simulation). To simulate how Hurricane Har-
vey will behave under future conditions, a storyline simula-
tion using SCREAM is performed (hereafter referred to as
the Pseudo Global Warming, PGW, simulation). In the PGW
simulation, the initial conditions and nudging data from
ERA5 are perturbed by adding the mean monthly changes
derived from a multi-model ensemble of climate simulations
from the Coupled Model Intercomparison Project Phase 6
(CMIP6) to represent the mean climate change under the
SSP5-8.5 scenario by the end of the 21st century (2079–
2099) compared to the historical climate at the end of the
20th century (1990–2010). A similar perturbation is also ap-
plied to ELM for the PGW simulations.

k=1UHF(k,:) · CHF(:,k). According to Eq. (3), the
error from the LSG model ERLSG can be deﬁned as ERLSG =
PK

KP

UHF(k,:) · [
CLSG(:,k).

k=1UHF(k,:) · CHF(:,k) −

k=1

2.2
Study site and ﬂood events

We used the Hurricane Harvey ﬂood event (hereafter re-
ferred to as Harvey) in the Houston area as a case study.
On 26 August 2017, Harvey made landfall along the mid-
Texas coast as a Category 4 hurricane. As one of the worst
hurricanes to hit the United States in recent history, Har-
vey brought record-breaking rainfall across the Houston
metropolitan area (Van Oldenborgh et al., 2017), causing
more than 80 fatalities and over USD 150 billion in economic
losses, mostly due to extraordinary ﬂooding (Emanuel, 2017;
Balaguru et al., 2018). Speciﬁcally, we selected the Buffalo
Bayou at Turning Basin as the study domain (Fig. 2), where
the selected RHM was recently validated at different resolu-
tions (Xu et al., 2025).

SCREAM can successfully predict the heavy precipita-
tion during Harvey’s landfalls in Texas on 26 August, but
its simulated precipitation during the subsequent landfalls on

#### 27 and 28 August is relatively muted (Fig. 3a), a well-known

challenge even for many weather forecasting models (Wang
et al., 2018; Yang et al., 2019a). Considering the high com-
putational cost of the SCREAM runs, we conducted three
PGW simulations to drive the ensemble ﬂood projections.
These simulations, each with slightly different initial con-
ditions, represent the uncertainty of the hurricane projection
due to internal variability at the weather timescale (Fig. 3f).
One PGW simulation is selected for LSG model validation.
Its temporal and spatial patterns of precipitation are shown
in Fig. 3a, b, and d, which are signiﬁcantly different from
the patterns of the benchmark precipitation (Fig. 3a–c) se-
lected for LSG model training. The simulation differences
reﬂect model uncertainty and the effects of climate change
on the hurricane. Correspondingly, the simulated peak water
depth from the HF RHM using the benchmark precipitation
is signiﬁcantly larger than that using the PGW precipitation
(Fig. 3e). The signiﬁcant difference in the benchmark and
PGW precipitation as well as that in ﬂood simulations sup-
ports the use of the latter as an out-of-sample test case, rel-
evant for projecting future ﬂooding. Additionally, the choice
of a PGW ﬂood event over a historical ﬂood event for valida-
tion aligns better with the application scenarios of our down-
scaling method that are ensemble ﬂood projections.

Precipitation during Hurricane Harvey (Fig. 3) is extracted
from the 1 km resolution Multi-Radar Multi-Sensor (MRMS)
precipitation dataset, which has a native temporal resolution
of 2 min (Zhang et al., 2016). To demonstrate the effective-
ness of our downscaling approach for ensemble ﬂood projec-
tions, we use a projected hurricane event (Hurricane Harvey-
like) under the high warming scenario – Shared Socioeco-
nomic Pathway SSP5-8.5 – as a test case (Fig. 3). The future
hurricane is simulated using the Energy Exascale Earth Sys-
tem Model (E3SM) with the novel Simple Cloud-Resolving
E3SM Atmosphere Model (SCREAM) conﬁguration (Cald-
well et al., 2021; Donahue et al., 2024). SCREAM is a
global atmospheric circulation model with a nonhydrostatic
dynamical core and parameterizations for atmospheric radia-
tive transfer, cloud microphysics, and boundary layer clouds
and turbulence (Caldwell et al., 2021). The SCREAM do-
main features a regionally reﬁned mesh (RRM) with 3.25 km
grid spacing over the east coast of the United States, includ-
ing the Gulf of Mexico and a signiﬁcant part of the Atlantic
Ocean, within a global domain that has 25 km grid spac-
ing outside the RRM. Nudging is applied to grid cells out-
side the RRM to constrain the atmospheric circulation us-

https://doi.org/10.5194/hess-29-3833-2025
Hydrol. Earth Syst. Sci., 29, 3833–3852, 2025

### Page 6

3838
Z. Tan et al.: An efﬁcient hybrid downscaling framework to estimate high-resolution river hydrodynamics

Figure 3. Comparison of the observed (MRMS) and simulated hourly precipitation during Harvey under the observed historical (SCREAM)
and projected future (PGW) conditions (a), comparison of the cumulative MRMS and PGW precipitation (b), and maps of the observed
cumulative precipitation during Harvey (c), the cumulative precipitation of the PGW simulation selected for the LSG model validation (d),
the difference between the simulated peak water depth from the HF RHM using MRMS and that using the PGW precipitation (e), and the
coefﬁcient of variation (CV) of the PGW simulated cumulative precipitation ensemble (f) in the study domain. The 7 d total precipitation for
the 500-year return period in the Houston area is marked in (b).

2.3
River hydrodynamic model

Sanders, 2006):

∂h

∂t + ∂(uh)

∂x
+ ∂(vh)

∂y
= q,
(4)

In this study, we chose the 2-D Overland Flow Model (OFM;
Kim et al., 2012) for river hydrodynamics modeling, which
was recently validated for the Harvey ﬂood simulations (Xu
et al., 2025). Brieﬂy, OFM is a ﬁnite-volume model that
implements the ﬁrst-order Godunov-type upwind scheme
on a triangular mesh and uses Roe’s approximate Riemann
solver to compute ﬂuxes between grid cells (Begnudelli and
Sanders, 2006). Later, Ivanov et al. (2021) improved OFM’s
computational efﬁciency by using the Portable, Extensible
Toolkit for Scientiﬁc Computation (PETSc; Balay et al.,
2019) software for model parallelization. Mathematically,
OFM solves the 2-D shallow water equations, which include
the terms of advection, bottom friction, and gravity but ig-
nore the terms of Coriolis and viscous forces (Begnudelli and



2gh2

u2h + 1

∂

∂(uh)

∂t
+

∂x

+ ∂(uvh)

∂y
= −gh∂zb

u2 + v2,
(5)

p

∂x −CDu

∂(vh)

∂t
+ ∂(uvh)

∂x



2gh2

v2h + 1

∂

∂y
= −gh∂zb

u2 + v2, (6)

p

+

∂y −CDv

where t is the time (s), h is the ﬂow depth (m), u and v are
the water velocity (ms−1) in the x and y direction under the

Hydrol. Earth Syst. Sci., 29, 3833–3852, 2025
https://doi.org/10.5194/hess-29-3833-2025

### Page 7

Z. Tan et al.: An efﬁcient hybrid downscaling framework to estimate high-resolution river hydrodynamics
3839

Cartesian coordinate system, q is the excess precipitation rate
(ms−1), g is the gravitational acceleration constant (ms−2),
zb is the bed elevation (m), and CD is the bed drag coefﬁcient
derived from Manning’s roughness n as CD = gn2h−1/3.

high-resolution simulations from the HF RHM is a demon-
stration of the effectiveness of the downscaling method.

In the study, the accuracy of the downscaled hydrodynam-
ics is evaluated using multiple metrics. Using the HF sim-
ulation as the reference, we calculate the root mean square
error (RMSE) of the simulated hourly ﬂow depth and veloc-
ity at each grid cell during the ﬂood event and the absolute
bias of the simulated ﬂow depth and velocity at each grid cell
during the ﬂood peak. These two metrics are used to evalu-
ate the spatial uncertainty of the downscaled estimates. The
average RMSE of all the grid cells is also calculated to high-
light the overall uncertainty of the downscaling. The tempo-
ral uncertainty of the downscaled hydrodynamics is assessed
using the Kling–Gupta efﬁciency (KGE) (Gupta et al., 2009),
which can evaluate the bias, correlation, and error variability
of the downscaling comprehensively. The KGE is calculated
at 19 USGS gauges (Fig. 2), which have been previously used
to validate the HF RHM (Xu et al., 2025).

We conﬁgure the OFM model on two variable-resolution
meshes, with the high-resolution conﬁguration serving as the
HF RHM and the low-resolution conﬁguration as the LF
RHM. The variable-resolution meshes are generated using a
Delaunay-based unstructured mesh generator, JIGSAW (En-
gwirda, 2017), which can reﬁne topographic features impor-
tant for shaping river ﬂow regimes, such as river channels
(Kim et al., 2022; Xu et al., 2022), ﬂoodplains (Yamazaki
et al., 2011; Schrapffer et al., 2020), and water manage-
ment structures (Schmutz and Moog, 2018). Speciﬁcally, the
high-resolution mesh has 664 724 grid cells over the study
domain, representing the main channels, tributaries, dams,
and other regular cells with resolutions of 30, 60, 30, and

#### 1000 m, respectively. In contrast, the low-resolution mesh

has only 14 536 grid cells over the study domain, represent-
ing the main channels, tributaries, and other regular cells with
a uniform resolution of 1000 m (except for dams, which are
resolved at 30 m) (Fig. 2). In both the high-resolution and
low-resolution meshes, the areas around two ﬂood control
reservoirs, Addicks and Barker’s Reservoir (Fig. 2), are re-
ﬁned to ensure more accurate ﬂood simulations. As indicated
in Xu et al. (2025), even though the simulation of stream-
ﬂow at the outlet is only moderately degraded, the use of a
coarser mesh severely deteriorates the model performance in
simulating inundation. The 30 m resolution digital elevation
model (DEM) from the National Elevation Database (NED)
was used to construct the topography of the RHM meshes.

3

#### Results


3.1
Validation of downscaled ﬂow depth

The trained LSG models can accurately predict the spatial
and temporal variabilities of ﬂow depth (Figs. 4 and 5) and
velocity (Figs. 6 and 7) for the PGW ﬂood event. First, the
results conﬁrm the effectiveness of the EOF analysis in ex-
tracting the signiﬁcant spatial and temporal modes of the 2-D
shallow water equations (Figs. S4 and S5 in the Supplement).
Notably, as indicated by the proportion of variance explained
by the speciﬁc modes, the signiﬁcant modes of ﬂow velocity
(Fig. S5) are less representative of its variability compared
to those of ﬂow depth (Fig. S4), likely due to the higher
nonlinearity of ﬂow velocity simulations. Second, the trained
LSG models perform remarkably well in reconstructing the
HF ECs of river hydrodynamics from the LF ECs for both
the training (Figs. S6 and S7 in the Supplement) and predic-
tion phases (Figs. S8 and S9 in the Supplement). This perfor-
mance is achieved despite substantial distinctions between
the HF and LF ECs. Consequently, the spatial and temporal
features of the high-resolution ﬂow depth and velocity are
well reproduced for both the training (Figs. S10–S13 in the
Supplement) and prediction phases (Figs. 4–7), even though
they are forced by two distinct hurricane events (Fig. 3).

To force the OFM, the MRMS precipitation data are up-
scaled from their native temporal resolution to an hourly
time step and spatially interpolated to the variable-resolution
mesh cells using the nearest-neighbor interpolation method.
Similarly, the hourly SCREAM simulation data are spa-
tially interpolated to the variable-resolution mesh cells using
the nearest-neighbor method before being used to force the

#### OFM.


2.4
Validation of downscaled hydrodynamics

Validation of the downscaling method uses the “perfect prog-
nosis” approach in which the HF RHM simulation is the
target for the downscaled ﬂow depth and velocity that uses
the LF RHM simulated ﬂow depth and velocity as the input.
This validation strategy allows one to focus on evaluating
the downscaling method without the inﬂuence of the RHM
or observation errors and has been widely adopted in cli-
mate downscaling (Denis et al., 2002) as well as hydrological
and hydrodynamic downscaling (Carreau and Guinot, 2021;
Feng et al., 2023b) when both low- and high-resolution simu-
lations are available. Therefore, in this study, good agreement
between the downscaled ﬂow depth and velocity with the

During the PGW ﬂood, using the HF simulation as the ref-
erence, the average RMSE of the downscaled ﬂow depth is

#### 0.07 ± 0.1 m (Fig. 4b), which is less than one-fourth of the

average RMSE (0.3 ± 0.6 m) of the simulated LF ﬂow depth
(Fig. 4a). The downscaling achieves impressive error reduc-
tions in river channels (particularly downstream reaches), the
nearby ﬂoodplains, and the two reservoirs (Fig. 4), which are
ﬂood-prone areas that have been deliberately reﬁned in the
high-resolution mesh (Fig. 2c). By downscaling, the detailed
longitudinal variations of ﬂow depth in the HF simulation

https://doi.org/10.5194/hess-29-3833-2025
Hydrol. Earth Syst. Sci., 29, 3833–3852, 2025

### Page 8

3840
Z. Tan et al.: An efﬁcient hybrid downscaling framework to estimate high-resolution river hydrodynamics

Figure 4. Root mean square error (RMSE) of the LF simulated (a) and downscaled ﬂow depth (b) for the entire PGW event, the LF
simulated (c) and downscaled ﬂow depth (d) at 01:00 CST on 27 August (the peak ﬂood time), the bias of the LF simulated (e) and downscaled
ﬂow depth (f) at the peak ﬂood time, and the HF simulated ﬂow depth (g) at the peak ﬂood time. RMSE and bias are calculated by treating
the HF simulation as “ground truth”.

scaled ﬂow depth achieves KGE ≥0.5 (good performance)
at all gauges except Gauge #14, where a small inunda-
tion occurs. In contrast, the LF simulation only achieves
KGE ≥0.5 at two gauges but exhibits poor performance
(KGE < −0.41; Knoben et al., 2019) at three gauges,
whereas the performance at the other gauges is barely ac-
ceptable (−0.41 < KGE < 0.5). Notably, for four gauges (#3,
#7, #8, and #19), the downscaling approach achieves KGE
≥0.9 (excellent performance). Not only does the downscal-
ing reduce the severe biases of the LF simulation at nearly all
gauges, but it also recovers dynamics not captured by the LF
simulation, such as the second peak ﬂow depth at Gauge #18.

(Fig. 4g) are precisely reproduced (Fig. 4d) during the peak
ﬂood period (near 01:00 CST, 27 August). Even very small
ponding grid cells, which are barely seen in the LF simula-
tion (Fig. 4c), are recovered (Fig. 4d). Compared to the LF
simulation, the downscaled ﬂow depth is highly consistent
with the HF simulation at the peak ﬂood time, with the bias
range (from the 10th percentile to the 90th percentile) re-
duced from [−0.2 m, 0.3 m] (Fig. 4e) to [−0.04 m, 0.06 m]
(Fig. 4f). Generally, the downscaling reduces the underesti-
mation and overestimation of the LF simulated ﬂow depth in
river channels and ﬂoodplains, respectively, likely due to the
use of the HF EOFs (Fig. S4).

The downscaling approach also performs promisingly in
reproducing the temporal variability of the HF simulated
ﬂow depth at the selected USGS gauges (Fig. 5). The down-

Hydrol. Earth Syst. Sci., 29, 3833–3852, 2025
https://doi.org/10.5194/hess-29-3833-2025

### Page 9

Z. Tan et al.: An efﬁcient hybrid downscaling framework to estimate high-resolution river hydrodynamics
3841

Figure 5. Comparison of the HF simulated, LF simulated, and downscaled ﬂow depth at the selected USGS gauges during the PGW event.

ﬂow velocity achieves KGE ≥0.5 (good performance) at

#### 15 gauges and KGE ≥0.9 (excellent performance) at two

gauges (#11 and #16). In contrast, the LF simulation only
achieves KGE ≥0.5 at Gauge #8 but exhibits unacceptable
performance (KGE < −0.41) at nine gauges. However, de-
spite its superiority to the LF simulation, the downscaled
ﬂow velocity does not perform as well as the downscaled
ﬂow depth at many of the study gauges. For instance, it fails
to capture the velocity spike at Gauge #1 and greatly under-
estimates the velocity peaks at several other gauges (e.g., #2,
#4, and #8). The downscaled solutions also struggle to repro-
duce the high-frequency ﬂuctuations of ﬂow velocity, such
as at Gauges #12 and #18. Analysis of the error sources in-
dicates that for the downscaled ﬂow velocity, the error from
dimensionality reduction ERDR is substantially larger than
the LSG model error ERLSG, while for the downscaled ﬂow
depth, ERLSG is dominant (Fig. 8). First, this result aligns
with the EOF analysis (Fig. S5), which shows the higher
nonlinearity of ﬂow velocity simulations. Second, this im-
plies that reducing ERDR is crucial for more accurate ﬂow
velocity downscaling.

3.2
Validation and enhancement of downscaled ﬂow
velocity

Likewise, the downscaled simulations provide accurate rep-
resentations of the spatial and temporal variabilities of
ﬂow velocity during the PGW ﬂood (Figs. 6 and 7). The
downscaling signiﬁcantly reduces the average RMSE of
simulated ﬂow velocity from 0.7 ± 1.9 ms−1 (Fig. 6a) to

#### 0.2 ± 0.6 ms−1 (Fig. 6b). Compared to ﬂow depth, the er-

ror reduction in ﬂow velocity is more concentrated in the
river channels, possibly reﬂecting the larger gradients of ﬂow
velocity from river channels to the nearby ﬂoodplains. Like
ﬂow depth, the downscaling successfully recovers the de-
tailed longitudinal variations of ﬂow velocity in the HF sim-
ulation (Fig. 6g), as well as the river ﬂow in small inundated
areas during the peak ﬂood period (Fig. 6d). The method
also yields substantial reductions in the estimation bias at
the peak ﬂood time, from [−0.4 ms−1, 0.3 ms−1] (Fig. 6e)
to [−0.07 ms−1, 0.05 ms−1] (Fig. 6f).

The downscaling also produces more consistent temporal
variability of ﬂow velocity compared with the HF simula-
tion at the selected USGS gauges (Fig. 7). The downscaled

https://doi.org/10.5194/hess-29-3833-2025
Hydrol. Earth Syst. Sci., 29, 3833–3852, 2025

### Page 10

3842
Z. Tan et al.: An efﬁcient hybrid downscaling framework to estimate high-resolution river hydrodynamics

Figure 6. RMSE of the LF simulated (a) and downscaled ﬂow velocity (b) for the entire PGW event, the LF simulated (c) and downscaled
ﬂow velocity (d) at 01:00 CST on 27 August (the peak ﬂood time), the bias of the LF simulated (e) and downscaled ﬂow velocity (f) at the
peak ﬂood time, and the HF simulated ﬂow velocity (g) at the peak ﬂood time. RMSE and bias are calculated by treating the HF simulation
as “ground truth”.

A possible way to reduce ERDR is to regionalize the train-
ing of the LSG model in a smaller domain that focuses on
a speciﬁc geographic feature. This approach can prevent lo-
cally important EC modes from being ﬁltered out in large-
scale EOF analyses (see Fraehr et al., 2023a, for North’s
test and Kaiser’s rule). Notably, this treatment does not re-
quire new model simulations and follows the same proce-
dure outlined in Fig. 1. We selected Gauge #1, where the
whole-domain downscaling fails to reproduce the peak ﬂow
velocity simulated by the HF model. By training a new LSG
model over a smaller area encompassing the gauge (Fig. S14
in the Supplement), the downscaled simulation aligns with
the HF model for predicting the ﬂow velocity spike on 26 Au-
gust (Fig. 9). For the PGW event, the KGE for the simulated
ﬂow velocity increases signiﬁcantly from 0.04 to 0.61. The

regionalized training also slightly improves the accuracy of
the downscaled ﬂow depth at Gauge #1, with KGE increasing
from 0.81 to 0.96. The smaller effect of regionalized training
on ﬂow depth is expected because our error analysis indicates
that the uncertainty of the downscaled ﬂow depth is only mi-
norly contributed by ERDR (Fig. 8).

3.3
Ensemble inundation downscaling

Because the training of the LSG model can be completed
within minutes, the computational cost of our downscaling
approach depends solely on the computational time needed
for the RHM simulations. For the 13 d PGW simulations,
when running on Intel Xeon Skylake CPUs (2.4 GHz) with

#### 192 GB of DDR4 DRAM, the HF model (664 724 grid cells)

requires 4032 CPU hours to complete, while the LF model

Hydrol. Earth Syst. Sci., 29, 3833–3852, 2025
https://doi.org/10.5194/hess-29-3833-2025

### Page 11

Z. Tan et al.: An efﬁcient hybrid downscaling framework to estimate high-resolution river hydrodynamics
3843

Figure 7. Comparison of the HF simulated, LF simulated, and downscaled ﬂow velocity at the selected USGS gauges during the PGW event.

4

#### Discussion


(14 536 grid cells) requires only 48 CPU hours. Thus, by ap-
plying the downscaling approach to the LF ensemble sim-
ulations, our method provides an efﬁcient way to evalu-
ate the impact of the uncertainty in tropical cyclone (TC)
predictions on the simulation of urban ﬂooding. Figure 10
shows that compared to the single-member PGW simula-
tion described in the above evaluation, a three-member en-
semble of PGW simulations predicts higher peak inundation
depths in the lower reaches of the Buffalo Bayou watershed,
where population density is also the highest. In some areas,
the difference in peak ﬂood depth during the PGW event
can exceed 1 m (Fig. 10b). Using the ensemble simulations,
we can also calculate the likelihood of the areas where the
PGW ﬂood event poses signiﬁcant or high risks to human
safety (h > 0.95 m; Russo et al., 2013). From the ensemble
simulations, humans will very likely face signiﬁcant risks
from ﬂoodwater in the two reservoirs, river channels, and
the nearby areas in Houston during the PGW ﬂood event
(Fig. 10c). In line with Fig. (10b), some simulations predict
larger extents of the areas where the ﬂood event would pose
signiﬁcant risks to human safety.

4.1
Simulation of high-resolution river hydrodynamics

Our results demonstrate that the LSG-model-based down-
scaling approach can provide efﬁcient and accurate simula-
tions of high-resolution river hydrodynamics at the computa-
tional cost of LF RHMs. To the best of our knowledge, this
is one of the ﬁrst studies to explore methods for fast and ac-
curate simulations of high-resolution ﬂow velocity in realis-
tic cases, broadening the usefulness and relevance of recent
rapid progress in hydrodynamic modeling, which still exclu-
sively focuses on ﬂooding (Carreau and Guinot, 2021; Xie
et al., 2021; Zhou et al., 2021; Feng et al., 2023b; Fraehr
et al., 2023b; Frame et al., 2024; Wing et al., 2024). With
HF simulations of ﬂow velocity, our understanding of not
only instantaneous ﬂood hazards but also longer-timescale
environmental hazards, such as eutrophication and pollution,
can be greatly advanced. More broadly, the new method can
contribute to the development of fully coupled atmosphere–
land–river–ocean ESMs, which will be discussed in detail
in Sect. 4.2. It is worth noting that the study watersheds of

https://doi.org/10.5194/hess-29-3833-2025
Hydrol. Earth Syst. Sci., 29, 3833–3852, 2025

### Page 12

3844
Z. Tan et al.: An efﬁcient hybrid downscaling framework to estimate high-resolution river hydrodynamics

Figure 8. Percentage of ﬂow depth (a) and velocity (b) downscaling uncertainty that can be explained by the error from the LSG model.

Figure 9. Comparison of the HF simulated, LF simulated, and downscaled ﬂow depth and velocity at Gauge #1 during the PGW event when
training LSG models in a focused area around the gauge (Fig. S14).

Fraehr et al. (2023a, 2023b) differ from this study in land
use and climate. The two Australian watersheds in Fraehr
et al. (2023a, 2023b) are dominated by rural and natural land-
scapes and are less affected by TCs. The success of the LSG
model in different domains underscores its broad geographi-
cal applicability.

The LSG-model-based downscaling approach has two ma-
jor advantages over neural network (NN)-based methods for
high-resolution river hydrodynamic modeling. First, com-
pared to NN-based methods (Tran et al., 2023), the training
time of the LSG method is negligible, requiring only one ex-
pensive HF RHM simulation for training. Second, because
physical laws have been explicitly coded in LF RHMs and

Hydrol. Earth Syst. Sci., 29, 3833–3852, 2025
https://doi.org/10.5194/hess-29-3833-2025

### Page 13

Z. Tan et al.: An efﬁcient hybrid downscaling framework to estimate high-resolution river hydrodynamics
3845

Figure 10. Projected peak ﬂood depth of the PGW ensemble simulation (a), the difference of the projected peak ﬂood depth between the
PGW ensemble simulation and the selected PGW simulation (b), and the probability of signiﬁcant risks to human safety from ﬂooding (c).

implicitly complied with in the spatial interpolation process,
the trained model can be expected to be transferable to future
unseen climate conditions. These advantages make the ap-
proach well-suited for ensemble projections of future ﬂood-
ing, which are crucial for robust assessment of ﬂood adapta-
tion and mitigation (Fig. 10) given the substantial uncertainty
of TC projections (Fig. 3). Another potential strength of our
approach is that it can directly beneﬁt from future advances
in RHMs. The development of better RHMs will provide

more accurate LF and HF simulations of river hydrodynam-
ics for LSG model training, helping to reduce downscaling
uncertainty (Fraehr et al., 2023a).

While a well-trained LSG model can be applied to un-
seen climate conditions, it is not free from retraining. For in-
stance, without retraining, an LSG model is unlikely to han-
dle changes in land use and geographical features, such as
geomorphological changes in river channels and river ﬂow
modiﬁcations related to reservoirs. Additionally, our training

https://doi.org/10.5194/hess-29-3833-2025
Hydrol. Earth Syst. Sci., 29, 3833–3852, 2025

### Page 14

3846
Z. Tan et al.: An efﬁcient hybrid downscaling framework to estimate high-resolution river hydrodynamics

4.2
Coupling large-scale hydrodynamical processes
with local processes in river models

strategy, which trains the LSG model only with data from
the Harvey ﬂood event, may not be effective in more com-
plex cases where ﬂoods are not always driven by TCs. For
instance, the main ﬂood mechanisms in the US Mid-Atlantic
watersheds include both rain-on-snow (ROS) and snowmelt
events that mainly occur in high-latitude areas (e.g., 1996
ROS ﬂood) and heavy rainfall from tropical cyclones (e.g.,
Hurricane Irene in 2011), extratropical systems, and convec-
tive systems (Smith et al., 2010; Li et al., 2021; Sun et al.,
2024). For such cases, it is necessary to follow the training
procedure of Fraehr et al. (2023a), selecting multiple repre-
sentative ﬂood events of different types for training. Since
the number of ﬂood mechanisms is limited, we expect that
the computational demand will still be manageable even if
the LSG model is applied to a watershed with diverse ﬂood
generation processes.

It is challenging to represent other physical, chemical, and bi-
ological processes beyond river discharge in large-scale river
models. This is mainly because, by sacriﬁcing process and
resolution accuracy for computational efﬁciency, these mod-
els cannot provide accurate simulations of high-resolution
ﬂow depth and velocity necessary for calculating local dy-
namics important for ﬂuvial processes (Bertagni et al., 2024),
such as sediment settling velocity (Li et al., 2022), bottom
shear stress and diffusivity (Chen et al., 2023), and green-
house gas outgassing velocity (Ulseth et al., 2019). By accu-
rately and efﬁciently simulating high-resolution ﬂow depth
and velocity, our downscaling approach provides an oppor-
tunity to bridge the gaps between large-scale hydrodynam-
ical processes and detailed local processes in river mod-
els. Speciﬁcally, we propose a two-way coupling scheme in
large-scale river models (Fig. 11). In the ﬁrst stage of each
simulation cycle, a large-scale river model is used to simu-
late coarse-resolution ﬂow depth and velocity and transport
mass and momentum downstream. In the second stage, the
LSG-model-based approach is employed to downscale the
simulated ﬂow depth and velocity to ﬁne resolutions. In the
third stage, high-resolution hydrodynamics are used to drive
detailed physical, chemical, and biological models, such as
the PFLOTRAN model for geochemistry (Hammond et al.,
2012) and the GAIA model for sediment (Tassi et al., 2023),
to simulate the sources and sinks of the represented tracers.
In the ﬁnal stage, the sources and sinks calculated in the ﬁne-
resolution mesh are upscaled to the coarse-resolution mesh
of the large-scale river model and used to update the concen-
trations of the represented tracers.

Our study reveals that the downscaling accuracy of ﬂow
velocity is lower than that of ﬂow depth. This is because
the dynamics of ﬂow velocity are more nonlinear, which
induces signiﬁcantly larger dimensionality-reduction errors
in the downscaling process (Fig. 8). Accordingly, we in-
troduced a regionalized training procedure to improve the
downscaled ﬂow velocity in focused areas (Fig. 9). This pro-
cedure does not signiﬁcantly increase the computational cost
of the LSG model because it does not require any new RHM
runs. We envision that this strategy can be particularly use-
ful for simulating river hydrodynamics in geographical ar-
eas that need more careful ﬂood risk assessments, such as
schools, hospitals, critical infrastructures, energy facilities,
and Superfund sites (Brand et al., 2018).

The LSG model error ERLSG primarily depends on the per-
formance of the sparse GP model in mapping LF ECs to HF
ECs. Besides the sparse GP model, other data-driven models,
such as multilayer perceptrons and artiﬁcial neural networks,
can also be used to establish the complex relationships be-
tween ECs (Carreau and Guinot, 2021). Future research on
implementing other data-driven models to reduce ERLSG is
also worth exploring.

An outstanding weakness of existing ESMs is that they
ignore the lateral biogeochemical ﬂuxes in the land–river–
ocean continuum and therefore do not close the global bio-
geochemical cycles (Regnier et al., 2022). By implementing
this new paradigm of river modeling in ESMs, land, river,
and ocean biogeochemistry will be fully coupled, helping
to close the global biogeochemical cycles. To achieve this
vision, future research must focus on extending the LSG-
model-based approach to downscale 1-D river models to 2-D
ﬁne-resolution meshes. This is because, despite the prospect
of 2-D large-scale river models running on GPU-based su-
percomputers, 1-D river models will likely still be the default
conﬁguration in ESMs in the near future (Telteu et al., 2021).
We envision that the potential challenges could include the
alignment of 1-D and 2-D unstructured meshes and the in-
terpolation of simulated 1-D river hydrodynamics onto 2-D
meshes.

The LF model used in this study is about 84 times faster
than the HF model, which is signiﬁcantly more efﬁcient than
the LF model adopted by Fraehr et al. (2023a) that is only

#### 12 times faster. Also, our LF model achieves a larger accel-

eration rate than the theoretical boost rate when considering
the reduction in the number of grid cells ( 664 724


#### 14 536 ≈46). The

improved efﬁciency indicates that the OFM RHM has taken
advantage of fewer computational units and longer time steps
according to the Courant–Friedrichs–Lewy convergence cri-
teria in the simulations. Furthermore, the results underscore
the usefulness of our approach for ﬂood risk assessment,
which needs hundreds or thousands of ensemble model runs
for uncertainty quantiﬁcation (Wu et al., 2020), which the
conﬁguration of Fraehr et al. (2023a) cannot provide due to
its inefﬁcient LF simulations.

Hydrol. Earth Syst. Sci., 29, 3833–3852, 2025
https://doi.org/10.5194/hess-29-3833-2025

### Page 15

Z. Tan et al.: An efﬁcient hybrid downscaling framework to estimate high-resolution river hydrodynamics
3847

Figure 11. A schematic illustration of coupling large-scale hydrodynamical processes that are simulated in coarse resolution with local
physical, chemical, and biological processes that are simulated in ﬁne resolution in river models.

5

#### Conclusion


gaps between large-scale hydrodynamical processes and lo-
cal physical, chemical, and biological processes in river mod-
els, which could eventually help close the global biogeo-
chemical cycles in ESMs.

In this study, we developed a downscaling approach based
on the LSG model to achieve fast and accurate simulations
of high-resolution river ﬂow depth and velocity. Our test of
TC-induced ﬂood events in an urban watershed in Houston
demonstrates the effectiveness and efﬁciency of the down-
scaling method, as the simulation errors in the LF RHM
are greatly reduced, without additional computational costs.
We further indicated that the simulation error of the down-
scaled ﬂow velocity can be reduced by employing region-
alized training of the LSG model for selected focus areas.
As one of the ﬁrst studies to explore high-ﬁdelity and ef-
ﬁcient ﬂow velocity simulations in realistic cases, our re-
search can help broaden the usefulness and relevance of
the recent rapid progress in hydrodynamic modeling, which
still exclusively focuses on ﬂooding. More importantly, the
downscaling approach provides an opportunity to bridge the

Code and data availability. The code and input data for this work
are publicly available at https://doi.org/10.5281/zenodo.14258083
(Tan, 2024–2025).

Supplement. The supplement related to this article is available on-
line at https://doi.org/10.5194/hess-29-3833-2025-supplement.

Author contributions. ZT, DX, and LRL designed the study. ZT de-
veloped the methodological framework and performed the formal
analyses, validation, and visualization of the results. DX, ST, JM,
and GB provided research resources. LRL performed funding ac-

https://doi.org/10.5194/hess-29-3833-2025
Hydrol. Earth Syst. Sci., 29, 3833–3852, 2025

### Page 16

3848
Z. Tan et al.: An efﬁcient hybrid downscaling framework to estimate high-resolution river hydrodynamics

quisition and project administration. ZT wrote the original paper
draft, and all co-authors reviewed and edited the paper.

Balay,

#### S.,

Abhyankar,

#### S.,

Adams,

#### M.,

Brown,

#### J.,

Brune,
P., Buschelman, K., Dalcin, L., Dener, A., Eijkhout, V.,
Gropp, W., Karpeyev, D., Kaushik, D., Knepley, M., May,
D., McInnes, L. C., Mills, R., Munson, T., Rupp, K.,
Sanan, P., Smith, B., Zampini, S., Zhang, H., and Zhang,
H.: PETSc User’s Manual, https://publications.anl.gov/anlpubs/
2019/12/155920.pdf (last access: 2 October 2024), 2019.
Bates, P. D.: Flood inundation prediction, Annu. Rev. Fluid Mech.,

Competing interests. The contact author has declared that none of
the authors has any competing interests.

54, 287–315, 2022.
Battin, T. J., Lauerwald, R., Bernhardt, E. S., Bertuzzo, E., Gener,

Disclaimer. Publisher’s note: Copernicus Publications remains
neutral with regard to jurisdictional claims made in the text, pub-
lished maps, institutional afﬁliations, or any other geographical rep-
resentation in this paper. While Copernicus Publications makes ev-
ery effort to include appropriate place names, the ﬁnal responsibility
lies with the authors.

L. G., Hall, R. O., Hotchkiss, E. R., Maavara, T., Pavelsky, T.
M., Ran, L., Raymond, P., Rosentreter, J. A., and Regnier, P.:
River ecosystem metabolism and carbon biogeochemistry in a
changing world, Nature, 613, 449–459, 2023.
Begnudelli, L. and Sanders, B. F.: Unstructured grid ﬁnite-volume

algorithm for shallow-water ﬂow and scalar transport with wet-
ting and drying, J. Hydraul. Eng., 132, 371–384, 2006.
Bermúdez, M., Cea, L., Van Uytven, E., Willems, P., Farfán, J.,


#### Acknowledgements. We thank the three anonymous reviewers for

their constructive comments. This study was supported by the US
Department of Energy Advanced Scientiﬁc Computing Research
(ASCR) program through the Multiphysics Simulations and Knowl-
edge discovery through AI/ML technologies (MuSiKAL) project.
It was also partly supported by the Scientiﬁc Discovery through
Advanced Computing 5 (Capturing the Dynamics of Compound
Flooding in E3SM) and the Integrated Coastal Modeling (ICoM)
project, funded by the US Department of Energy, Ofﬁce of Sci-
ence, Ofﬁce of Biological and Environmental Research as part
of the Earth System Model Development (ESMD) and Regional
and Global Model Analysis (RGMA) program areas, respectively.
The Paciﬁc Northwest National Laboratory (PNNL) is operated
by Battelle for the US Department of Energy under contract DE-
AC05-76RLO1830. All model simulations were performed using
resources available through (a) Research Computing at PNNL and
(b) the National Energy Research Scientiﬁc Computing Center
(NERSC), a US Department of Energy Ofﬁce of Science User Facil-
ity located at Lawrence Berkeley National Laboratory, operated un-
der contract no. DE-AC02-05CH11231 using NERSC award BER-

#### ERCAP0027117.


and Puertas, J.: A robust method to update local river inunda-
tion maps using global climate model output and weather typing
based statistical downscaling, Water Resour. Manag., 34, 4345–
4362, 2020.
Bertagni, M. B., Regnier, P., Yan, Y., and Porporato, A.: A

dimensionless framework for the partitioning of ﬂuvial in-
organic carbon, Geophys. Res. Lett., 51, e2024GL111310,
https://doi.org/10.1029/2024GL111310, 2024.
Brand,
J.

#### H.,

Spencer,
K.

#### L.,

O’Shea,
F.

#### T.,

and
Lind-
say, J. E.: Potential pollution risks of historic landﬁlls on
low-lying coasts and estuaries, WIREs Water, 5, e1264,
https://doi.org/10.1002/wat2.1264, 2018.
Caldwell, P. M., Terai, C. R., Hillman, B., Keen, N. D., Bo-

genschutz, P., Lin, W., Beydoun, H., Taylor, M., Bertagna, L.,
Bradley, A. M., Clevenger, T. C., Donahue, A. S., Eldred, C.,
Foucar, J., Golaz, J.-C., Guba, O., Jacob, R., Johnson, J., Krishna,
J., Liu, W., Pressel, K., Salinger, A. G., Singh, B., Steyer, A., Ull-
rich, P., Wu, D., Yuan, X., Shpund, J., Ma, H.-Y., and Zender, C.
S.: Convection-permitting simulations with the E3SM global at-
mosphere model, J. Adv. Model. Earth Sy., 13, e2021MS002544,
https://doi.org/10.1029/2021MS002544, 2021.
Carpenter, S. R., Stanley, E. H., and Vander Zanden, M. J.: State

Financial support. This research has been supported by the US De-
partment of Energy (Multiphysics Simulations and Knowledge dis-
covery through AI/ML technologies (MuSiKAL), Scientiﬁc Dis-
covery through Advanced Computing 5 (Capturing the Dynamics
of Compound Flooding in E3SM), and Integrated Coastal Model-
ing (ICoM)).

of the world’s freshwater ecosystems: physical, chemical, and
biological changes, Annu. Rev. Environ. Resour., 36, 75–99,
https://doi.org/10.1146/annurev-environ-021810-094524, 2011.
Carreau, J. and Guinot, V.: A PCA spatial pattern based ar-

tiﬁcial neural network downscaling model for urban ﬂood
hazard
assessment,
Adv.
Water
Resour.,
147,
103821,
https://doi.org/10.1016/j.advwatres.2020.103821, 2021.
Chen, K., Chen, H., Zhou, C., Huang, Y., Qi, X., Shen, R.,

Review statement. This paper was edited by Christa Kelleher and
reviewed by three anonymous referees.

Liu, F., Zuo, M., Zou, X., Wang, J., Zhang, Y., Chen, D.,
Chen, X., Deng, Y., and Ren, H.: Comparative analysis of
surface water quality prediction performance and identiﬁca-
tion of key water parameters using different machine learn-
ing models based on big data, Water Res., 171, 115454,
https://doi.org/10.1016/j.watres.2019.115454, 2020.
Chen, K., Yang, S., Roden, E. E., Chen, X., Chang, K.-Y., Guo,


#### References


Allen, G. H. and Pavelsky, T. M.: Global extent of rivers and

Z., Liang, X., Ma, E., Fan, L., and Zheng, C.: Inﬂuence of ver-
tical hydrologic exchange ﬂow, channel ﬂow, and biogeochemi-
cal kinetics on CH4 emissions from rivers, Water Resour. Res.,

streams, Science, 361, 585–588, 2018.
Balaguru, K., Foltz, G. R., and Leung, L. R.: Increasing magnitude

of hurricane rapid intensiﬁcation in the central and eastern tropi-
cal Atlantic, Geophys. Res. Lett., 45, 4238–4247, 2018.

Hydrol. Earth Syst. Sci., 29, 3833–3852, 2025
https://doi.org/10.5194/hess-29-3833-2025

### Page 17

Z. Tan et al.: An efﬁcient hybrid downscaling framework to estimate high-resolution river hydrodynamics
3849

59, e2023WR035341, https://doi.org/10.1029/2023WR035341,
2023.
Denis, B., Laprise, R., Caya, D., and Côté, J.: Downscaling abil-

Freer, J., Beven, K. J., Neal, J., Schumann, G., Hall, J., and Bates, P.:

Flood risk and uncertainty, in: Risk and Uncertainty Assessment
for Natural Hazards, Cambridge, Cambridge University Press,

#### 190–233, ISBN 978-1-107-00619-5, 2011.

Gadgil, A.: Drinking water in developing countries, Annu. Rev. En-

ity of one-way nested regional climate models: the Big-Brother
Experiment, Clim. Dynam., 18, 627–646, 2002.
Donahue, A. S., Caldwell, P. M., Bertagna, L., Beydoun, H., Bo-

erg. Env., 23, 253–286, 1998.
Gao, S., Huang, Y., Zhang, S., Han, J., Wang, G., Zhang,

genschutz, P. A., Bradley, A. M., Clevenger, T. C., Foucar, J.,
Golaz, C., Guba, O., Hannah, W., Hillman, B. R., Johnson, J. N.,
Keen, N., Lin, W., Singh, B., Sreepathi, S., Taylor, M. A., Tian, J.,
Terai, C. R., Ullrich, P. A., Yuan, X., and Zhang, Y.: To exascale
and beyond – The Simple Cloud-Resolving E3SM Atmosphere
Model (SCREAM), a performance portable global atmosphere
model for cloud-resolving scales, J. Adv. Model. Earth Sy.,
16, e2024MS004314, https://doi.org/10.1029/2024MS004314,
2024.
Emanuel, K.: Assessing the present and future probability of Hur-

M., and Lin, Q.: Short-term runoff prediction with GRU
and LSTM networks without requiring time step optimiza-
tion during sample generation, J. Hydrol., 589, 125188,
https://doi.org/10.1016/j.jhydrol.2020.125188, 2020.
Gupta, H. V., Kling, H., Yilmaz, K. K., and Martinez, G. F.: Decom-

position of the mean squared error and NSE performance criteria:
Implications for improving hydrological modelling, J. Hydrol.,
377, 80–91, 2009.
Ha, S., Liu, D., and Mu, L.: Prediction of Yangtze River

ricane Harvey’s rainfall, P. Natl. Acad. Sci. USA, 114, 12681–
12684, 2017.
Engwirda, D.: JIGSAW-GEO (1.0): locally orthogonal stag-

streamﬂow based on deep learning neural network with
El
Niño–Southern
Oscillation,
Sci.
Rep.,
11,
11738,
https://doi.org/10.1038/s41598-021-90964-3, 2021.
Haddeland, I., Lettenmaier, D. P., and Skaugen, T.: Effects of ir-

gered unstructured grid generation for general circulation mod-
elling on the sphere, Geosci. Model Dev., 10, 2117–2140,
https://doi.org/10.5194/gmd-10-2117-2017, 2017.
Feng, D., Tan, Z., Engwirda, D., Liao, C., Xu, D., Bisht, G., Zhou,

rigation on the water and energy balances of the Colorado and
Mekong river basins, J. Hydrol., 324, 210–223, 2006.
Hammond, G. E., Lichtner, P. C., Lu, C., and Mills, R. T.: PFLO-

T., Li, H.-Y., and Leung, L. R.: Investigating coastal backwater
effects and ﬂooding in the coastal zone using a global river trans-
port model on an unstructured mesh, Hydrol. Earth Syst. Sci., 26,
5473–5491, https://doi.org/10.5194/hess-26-5473-2022, 2022.
Feng, D., Tan, Z., Xu, D., and Leung, L. R.: Understand-

TRAN: Reactive ﬂow and transport code for use on laptops to
leadership-class supercomputers, Groundwater Reactive Trans-
port Models, 5, 141–159, 2012.
He,

#### Q.,

Barajas-Solano,

#### D.,

Tartakovsky,

#### G.,

and
Tar-
takovsky,
A.

#### M.:

Physics-informed
neural
networks
for
multiphysics
data
assimilation
with
application
to
subsurface
transport,
Adv.
Water
Res.,
141,
103610,
https://doi.org/10.1016/j.advwatres.2020.103610, 2020.
Hersbach, H., Bell, B., Berrisford, P., Hirahara, S., Horányi, A.,

ing the compound ﬂood risk along the coast of the contigu-
ous United States, Hydrol. Earth Syst. Sci., 27, 3911–3934,
https://doi.org/10.5194/hess-27-3911-2023, 2023a.
Feng, D., Tan, Z., and He, Q.: Physics-informed neural net-

works of the Saint-Venant equations for downscaling a large-
scale river model, Water Resour. Res., 59, e2022WR033168,
https://doi.org/10.1029/2022WR033168, 2023b.
Feng, D., Tan, Z., Engwirda, D., Wolfe, J. D., Xu, D., Liao,

Muñoz-Sabater, J., Nicolas, J., Peubey, C., Radu, R., Schepers,
D., Simmons, A., Soci, C., Abdalla, S., Abellan, X., Balsamo, G.,
Bechtold, P., Biavati, G., Bidlot, J., Bonavita, M., De Chiara, G.,
Dahlgren, P., Dee, D., Diamantakis, M., Dragani, R., Flemming,
J., Forbes, R., Fuentes, M., Geer, A., Haimberger, L., Healy, S.,
Hogan, R. J., Hólm, E., Janisková, M., Keeley, S., Laloyaux, P.,
Lopez, P., Lupu, C., Radnoti, G., de Rosnay, P., Rozum, I., Vam-
borg, F., Villaume, S., and Thépaut, J.-N.: The ERA5 global re-
analysis, Q. J. Roy. Meteor. Soc., 146, 1999–2049, 2020.
Hostache, R., Hissler, C., Matgen, P., Guignard, C., and Bates,

C., Bisht, G., Benedict, J. J., Zhou, T., Li, H., and Le-
ung, L. R.: Simulation of compound ﬂooding using river-
ocean two-way coupled E3SM ensemble on variable-resolution
meshes, J. Adv. Model. Earth Sy., 16, e2023MS004054,
https://doi.org/10.1029/2023MS004054, 2024.
Fraehr, N., Wang, Q. J., Wu, W., and Nathan, R.: Upskilling low-

ﬁdelity hydrodynamic models of ﬂood inundation through Spa-
tial analysis and Gaussian Process learning, Water Resour. Res.,
58, e2022WR032248, https://doi.org/10.1029/2022WR032248,
2022.
Fraehr, N., Wang, Q. J., Wu, W., and Nathan, R.: Development

P.: Modelling suspended-sediment propagation and related
heavy metal contamination in ﬂoodplains: a parameter sen-
sitivity analysis, Hydrol. Earth Syst. Sci., 18, 3539–3551,
https://doi.org/10.5194/hess-18-3539-2014, 2014.
Hu,

#### X.,

Shi,

#### L.,

Lin,

#### G.,

and
Lin,

#### L.:

Comparison
of
physical-based, data-driven and hybrid modeling approaches
for evapotranspiration estimation, J. Hydrol., 601, 126592,
https://doi.org/10.1016/j.jhydrol.2021.126592, 2021.
Huang, S., Xia, J., Wang, Y., Wang, W., Zeng, S., She, D.,

of a fast and accurate hybrid model for ﬂoodplain inunda-
tion simulations, Water Resour. Res., 59, e2022WR033836,
https://doi.org/10.1029/2022WR033836, 2023a.
Fraehr, N., Wang, Q. J., Wu, W., and Nathan, R.: Supercharging

hydrodynamic inundation models for instant ﬂood insight, Nat.
Water, 1, 835–843, 2023b.
Frame, J. M., Nair, T., Sunkara, V., Popien, P., Chakrabarti,

and Wang, G.: Coupling machine learning into hydrody-
namic models to improve river modeling with complex bound-
ary conditions, Water Resour. Res., 58, e2022WR032183,
https://doi.org/10.1029/2022WR032183, 2022.
Ibáñez, C. and Peñuelas, J.: Changing nutrients, changing rivers,

S., Anderson, T., Leach, N. R., Doyle, C., Thomas, M., and
Tellman, B.: Rapid inundation mapping using the US Na-
tional Water Model, satellite observations, and a convolutional
neural network, Geophys. Res. Lett., 51, e2024GL109424,
https://doi.org/10.1029/2024GL109424, 2024.

Science, 365, 637–638, 2019.

https://doi.org/10.5194/hess-29-3833-2025
Hydrol. Earth Syst. Sci., 29, 3833–3852, 2025

### Page 18

3850
Z. Tan et al.: An efﬁcient hybrid downscaling framework to estimate high-resolution river hydrodynamics

IPCC.: Climate change 2021: The physical science basis. Contri-

morphological parameters and river ﬂow representation, Geosci.
Model Dev., 10, 1233–1259, https://doi.org/10.5194/gmd-10-
1233-2017, 2017.
Mao, Y., Zhou, T., Leung, L. R., Tesfa, T. K., Li, H.-Y., Wang, K.,

bution of working group I to the sixth assessment report of the
intergovernmental panel on climate change, C. U. Press, 2021.
Ivanov, V. Y., Xu, D., Dwelle, M. C., Sargsyan, K., Wright, D. B.,

Katopodes, N., Kim, J., Tran, V. N., Warnock, A., Fatichi, S.,
Burlando, P., Caporali, E., Restrepo, P., Sanders, B. F., Chaney,
M. M., Nunes, A. M. B., Nardi, F., Vivoni, E. R., Istanbulluoglu,
E., Bisht, G., and Bras, R. L.: Breaking down the computational
barriers to real-time urban ﬂood forecasting, Geophys. Res. Lett.,
48, e2021GL093585, https://doi.org/10.1029/2021GL093585,
2021.
Kaiser, H. F.: The application of electronic computers to factor anal-

Tan, Z., and Getirana, A.: Flood inundation generation mech-
anisms and their changes in 1953–2004 in global major river
basins, J. Geophys. Res.-Atmos., 124, 11672–11692, 2019.
Mishra, V. and Shah, H.: Hydroclimatological perspective of the

Kerala Flood of 2018, J. Geol. Soc. India, 92, 645–650, 2018.
North, G. R., Bell, T. L., Cahalan, R. F., and Moeng, F. J.: Sampling

errors in the estimation of empirical orthogonal functions, Mon.
Weather Rev., 110, 699–706, 1982.
Oki, T. and Kanae, S.: Global hydrological cycles and world water

ysis, Educ. Psychol. Meas., 20, 141–151, 1960.
Karniadakis, G. E., Kevrekidis, I. G., Lu, L., Perdikaris, P., Wang,

resources, Science, 313, 1068–1073, 2006.
Rasmussen, C. E. and Williams, C. K. I.: Gaussian processes for

S., and Yang, L.: Physics-informed machine learning, Nat. Rev.
Phys., 3, 422–440, 2021.
Kim, D.-W., Chung, E. G., Kim, K., and Kim, Y.: Impact of riverbed

machine learning, MIT Press, ISBN 0-262-18253-X, 2006.
Raymond, P. A., Saiers, J. E., and Sobczak, W. V.: Hydrological and

topography on hydrology in small watersheds using soil and
water assessment tool, Environ. Model. Softw., 152, 105383,
https://doi.org/10.1016/j.envsoft.2022.105383, 2022.
Kim, J., Warnock, A., Ivanov, V. Y., and Katopodes, N. D.: Coupled

biogeochemical controls on watershed dissolved organic matter
transport: Pulse-shunt concept, Ecology, 97, 5–16, 2016.
Razavi, S., Tolson, B. A., and Burn, D. H.: Review of surrogate

modeling in water resources, Water Resour. Res., 48, W07401,
https://doi.org/10.1029/2011WR011527, 2012.
Regnier, P., Resplandy, L., Najjar, R. G., and Ciais, P.: The land-to-

modeling of hydrologic and hydrodynamic processes including
overland and channel ﬂow, Adv. Water Resour., 37, 104–126,
2012.
Knoben, W. J. M., Freer, J. E., and Woods, R. A.: Technical note: In-

ocean loops of the global carbon cycle, Nature, 603, 401–410,
2022.
Rocher-Ros, G., Stanley, E. H., Loken, L. C., Casson, N. J., Ray-

herent benchmark or not? Comparing Nash–Sutcliffe and Kling–
Gupta efﬁciency scores, Hydrol. Earth Syst. Sci., 23, 4323–4331,
https://doi.org/10.5194/hess-23-4323-2019, 2019.
Konapala, G., Kao, S.-C., Painter, S. L., and Lu, D.: Machine

mond, P. A., Liu, S., Amatulli, G., and Sponseller, R. A.: Global
methane emissions from rivers and streams, Nature, 621, 530–
535, 2023.
Russo, B., Gómez, M., and Macchione, F.: Pedestrian hazard crite-

learning assisted hybrid models can improve streamﬂow sim-
ulation in diverse catchments across the conterminous US,
Environ. Res. Lett., 15, 104022, https://doi.org/10.1088/1748-
9326/aba927, 2020.
Li, H., Wigmosta, M. S., Wu, H., Huang, M., Ke, Y., Coleman, A.

ria for ﬂooded urban areas, Nat. Hazards, 69, 251–265, 2013.
Saha,
G.

#### K.,

Rahmani,

#### F.,

Shen,

#### C.,

Li,

#### L.,

and
Cibin,

#### R.:

A
deep
learning-based
novel
approach
to
generate
continuous
daily
stream
nitrate
concentration
for
nitrate
data-sparse watersheds, Sci. Total Environ., 878, 162930,
https://doi.org/10.1016/j.scitotenv.2023.162930, 2023.
Schmutz, S. and Moog, O.: Dams: Ecological Impacts and Man-

M., and Leung, L. R.: A physically based runoff routing model
for land surface and earth system models, J. Hydrometeorol., 14,
808–828, 2013.
Li, H.-Y., Tan, Z., Ma, H., Zhu, Z., Abeshu, G. W., Zhu, S.,

agement, in: Riverine ecosystem management: Science for gov-
erning towards a sustainable future, edited by: Schmutz, S. and
Sendzimir, J., Springer International Publishing, Cham, 111–
127, https://doi.org/10.1007/978-3-319-73250-3_6, 2018.
Schrapffer, A., Sörensson, A., Polcher, J., and Fita, L.: Beneﬁts

Cohen, S., Zhou, T., Xu, D., and Leung, L. R.: A new
large-scale suspended sediment model and its application over
the United States, Hydrol. Earth Syst. Sci., 26, 665–688,
https://doi.org/10.5194/hess-26-665-2022, 2022.
Li, J., Qian, Y., Leung, L. R., and Feng, Z.: Summer mean and

of representing ﬂoodplains in a Land Surface Model: Pantanal
simulated with ORCHIDEE CMIP6 version, Clim. Dynam., 55,
1303–1323, 2020.
Shabani, A., Woznicki, S. A., Mehaffey, M., Butcher, J., Wool, T.

extreme precipitation over the Mid-Atlantic region: Climato-
logical characteristics and contributions from different precip-
itation types, J. Geophys. Res.-Atmos., 126, e2021JD035045,
https://doi.org/10.1029/2021JD035045, 2021.
Liang, C., Li, H., Lei, M., and Du, Q.: Dongting lake water

A., and Whung, P. Y.: A coupled hydrodynamic (HEC-RAS 2D)
and water quality model (WASP) for simulating ﬂood-induced
soil, sediment, and contaminant transport, J. Flood Risk Manag.,
14, e12747, https://doi.org/10.1111/jfr3.12747, 2021.
Sherwood, S. C., Bony, S., and Dufresne, J.-L.: Spread in model

level forecast and its relationship with the three gorges dam
based on a long short-term memory network, Water, 10, 1389,
https://doi.org/10.3390/w10101389, 2018.
Liao, C., Zhou, T., Xu, D., Barnes, R., Bisht, G., Li, H.-

climate sensitivity traced to atmospheric convective mixing, Na-
ture, 505, 37–42, 2014.
Sikorska-Senoner, A. E. and Quilty, J. M.: A novel ensemble-

Y., Tan, Z., Tesfa, T., Duan, Z., Engwirda, D., and Le-
ung, L. R.: Advances in hexagon mesh-based ﬂow di-
rection
modeling,
Adv.
Water
Resour.,
160,
104099,
https://doi.org/10.1016/j.advwatres.2021.104099, 2022.
Luo, X., Li, H.-Y., Leung, L. R., Tesfa, T. K., Getirana, A., Papa,

based conceptual-data-driven approach for improved stream-
ﬂow
simulations,
Environ.
Model.
Softw.,
143,
105094,
https://doi.org/10.1016/j.envsoft.2021.105094, 2021.

F., and Hess, L. L.: Modeling surface water dynamics in the
Amazon Basin using MOSART-Inundation v1.0: impacts of geo-

Hydrol. Earth Syst. Sci., 29, 3833–3852, 2025
https://doi.org/10.5194/hess-29-3833-2025

### Page 19

Z. Tan et al.: An efﬁcient hybrid downscaling framework to estimate high-resolution river hydrodynamics
3851

Smith, J. A., Baeck, M. L., Villarini, G., and Krajewski, W. F.: The

Wilby, R. L. and Dawson, C. W.: The statistical downscaling model:

hydrology and hydrometeorology of ﬂooding in the Delaware
River Basin, J. Hydrometeorol., 11, 841–859, 2010.
Sukhodolov, A. N., Shumilova, O. O., Constantinescu, G. S., Lewis,

Insights from one decade of application, Int. J. Climatol., 33,
1707–1719, 2013.
Wing, O. E. J., Bates, P. D., Quinn, N. D., Savage, J. T. S., Uhe, P.

Q. W., and Rhoads, B. L.: Mixing dynamics at river conﬂu-
ences governed by intermodal behaviour, Nat. Geosci., 16, 89–
93, 2023.
Sun, N., Wigmosta, M. S., Yan, H., Eldardiry, H., Yang,

F., Cooper, A., Collings, T. P., Addor, N., Lord, N. S., Hatchard,
S., Hoch, J. M., Bates, J., Probyn, I., Himsworth, S., Rodríguez
González, J., Brine, M. P., Wilkinson, H., Sampson, C. C., Smith,
A. M., Neal, J. C., and Haigh, I. D.: A 30 m global ﬂood in-
undation model for any climate scenario, Water Resour. Res.,
60, e2023WR036460, https://doi.org/10.1029/2023WR036460,
2024.
Wu, H., Kimball, J. S., Mantua, N., and Stanford, J.: Au-

Z., Deb, M., Wang, T., and Judi, D.: Ampliﬁed Extreme
Floods and Shifting Flood Mechanisms in the Delaware River
Basin in Future Climates, Earths Future, 12, e2023EF003868,
https://doi.org/10.1029/2023EF003868, 2024.
Syvitski, J. P. M., Vörösmarty, C. J., Kettner, A. J., and Green, P.:

tomated upscaling of river networks for macroscale hy-
drological
modeling,
Water
Resour.
Res.,
47,

#### W03517,

https://doi.org/10.1029/2009WR008871, 2011.
Wu, W. Y., Emerton, R., Duan, Q. Y., Wood, A. W., Wetter-

Impact of humans on the ﬂux of terrestrial sediment to the global
coastal ocean, Science, 308, 376–380, 2005.
Tan, Z.: An efﬁcient hybrid downscaling framework to estimate

high-resolution river hydrodynamics, Zenodo [code and data
set], https://doi.org/10.5281/zenodo.14258083, 2024–2025.
Tassi,

#### P.,

Benson,

#### T.,

Delinares,

#### M.,

Fontaine,

#### J.,

Huy-
brechts, N., Kopmann, R., Pavan, S., Pham, C. T., Tac-
cone, F., and Walther, R.: GAIA – a uniﬁed framework
for sediment transport and bed evolution in rivers, coastal
seas and transitional waters in the TELEMAC-MASCARET
modelling system, Environ. Model. Softw., 159, 105544,
https://doi.org/10.1016/j.envsoft.2022.105544, 2023.
Telteu, C.-E., Müller Schmied, H., Thiery, W., Leng, G., Burek,

hall, F., and Robertson, D. E.: Ensemble ﬂood forecasting: Cur-
rent status and future opportunities, WIREs Water, 7, e1432,
https://doi.org/10.1002/wat2.1432, 2020.
Wunsch,

#### A.,

Liesch,

#### T.,

and
Broda,

#### S.:

Deep
learning
shows
declining
groundwater
levels
in
Germany
until

#### 2100 due to climate change, Nat. Commun., 13, 1221,

https://doi.org/10.1038/s41467-022-28770-2, 2022.
Xie, S., Wu, W., Mooser, S., Wang, Q. J., Nathan, R., and

Huang, Y.: Artiﬁcial neural network based hybrid modeling ap-
proach for ﬂood inundation modeling, J. Hydrol., 592, 125605,
https://doi.org/10.1016/j.jhydrol.2020.125605, 2021.
Xu, D., Bisht, G., Zhou, T., Leung, L. R., and Pan, M.:

P., Liu, X., Boulange, J. E. S., Andersen, L. S., Grillakis, M.,
Gosling, S. N., Satoh, Y., Rakovec, O., Stacke, T., Chang, J.,
Wanders, N., Shah, H. L., Trautmann, T., Mao, G., Hanasaki, N.,
Koutroulis, A., Pokhrel, Y., Samaniego, L., Wada, Y., Mishra, V.,
Liu, J., Döll, P., Zhao, F., Gädeke, A., Rabin, S. S., and Herz,
F.: Understanding each other’s models: an introduction and a
standard representation of 16 global water models to support
intercomparison, improvement, and communication, Geosci.
Model Dev., 14, 3843–3878, https://doi.org/10.5194/gmd-14-
3843-2021, 2021.
Teng, J., Jakeman, A. J., Vaze, J., Croke, B. F. W., Dutta, D., and

Development of land-river two-way hydrologic coupling for
ﬂoodplain inundation in the Energy Exascale Earth Sys-
tem Model, J. Adv. Model. Earth Sy., 14, e2021MS002772,
https://doi.org/10.1029/2021MS002772, 2022.
Xu, D., Bisht, G., Engwirda, D., Feng, D., Tan, Z., and Ivanov,

V. Y.: Uncertainties in simulating ﬂooding during Hurricane
Harvey using 2D shallow water equations, Water Resour. Res.,
61, e2024WR038032, https://doi.org/10.1029/2024WR038032,
2025.
Yamazaki, D., Kanae, S., Kim, H., and Oki, T.: A physically

Kim, S.: Flood inundation modelling: A review of methods, re-
cent advances and uncertainty analysis, Environ. Model. Softw.,
90, 201–216, 2017.
Tran, V. N., Ivanov, V. Y., Xu, D., and Kim, J.: Closing in on hy-

based description of ﬂoodplain inundation dynamics in a global
river routing model, Water Resour. Res., 47, 2010WR009726,
https://doi.org/10.1029/2010WR009726, 2011.
Yang, L., Smith, J., Liu, M., and Baeck, M. L.: Extreme rainfall

drologic predictive accuracy: Combining the strengths of high-
ﬁdelity and physics-agnostic models, Geophys. Res. Lett., 50,
e2023GL104464, https://doi.org/10.1029/2023GL104464, 2023.
Ulseth, A. J., Hall Jr, R. O., Boix Canadell, M., Madinger, H. L.,

from Hurricane Harvey (2017): Empirical intercomparisons of
WRF simulations and polarimetric radar ﬁelds, Atmos. Res.,
223, 114–131, 2019a.
Yang, S., Yang, D., Chen, J., and Zhao, B.: Real-time reservoir

Niayifar, A., and Battin, T. J.: Distinct air–water gas exchange
regimes in low- and high-energy streams, Nat. Geosci., 12, 259–
263, 2019.
Van Oldenborgh, G. J., Van Der Wiel, K., Sebastian, A., Singh,

operation using recurrent neural networks and inﬂow forecast
from a distributed hydrological model, J. Hydrol., 579, 124229,
https://doi.org/10.1016/j.jhydrol.2019.124229, 2019b.
Young, C.-C., Liu, W.-C., and Wu, M.-C.: A physically based and

R., Arrighi, J., Otto, F., Haustein, K., Li, S., Vecchi, G.,
and Cullen, H.: Attribution of extreme rainfall from Hurri-
cane Harvey, August 2017, Environ. Res. Lett., 12, 124009,
https://doi.org/10.1088/1748-9326/aa9ef2, 2017.
Wang, S.-Y. S., Zhao, L., Yoon, J.-H., Klotzbach, P., and Gillies, R.

machine learning hybrid approach for accurate rainfall-runoff
modeling during extreme typhoon events, Appl. Soft Comput.,
53, 205–216, 2017.
Zhang, D., Lin, J., Peng, Q., Wang, D., Yang, T., Sorooshian, S.,

R.: Quantitative attribution of climate effects on Hurricane Har-
vey’s extreme rainfall in Texas, Environ. Res. Lett., 13, 054014,
https://doi.org/10.1088/1748-9326/aabb85, 2018.

Liu, X., and Zhuang, J.: Modeling and simulating of reservoir op-
eration using the artiﬁcial neural network, support vector regres-
sion, deep learning algorithm, J. Hydrol., 565, 720–736, 2018.
Zhang, J., Howard, K., Langston, C., Kaney, B., Qi, Y., Tang, L.,

Grams, H., Wang, Y., Cocks, S., Martinaitis, S., Arthur, A.,

https://doi.org/10.5194/hess-29-3833-2025
Hydrol. Earth Syst. Sci., 29, 3833–3852, 2025

### Page 20

3852
Z. Tan et al.: An efﬁcient hybrid downscaling framework to estimate high-resolution river hydrodynamics

Cooper, K., Brogden, J., and Kitzmiller, D.: Multi-Radar Multi-
Sensor (MRMS) Quantitative Precipitation Estimation: Initial
Operating Capabilities, B. Am. Meteorol. Soc., 97, 621–638,
2016.
Zhang, Q., Ye, X., Werner, A. D., Li, Y., Yao, J., Li, X., and Xu, C.:

Zhou, Y., Wu, W., Nathan, R., and Wang, Q. J.: A rapid ﬂood in-

undation modelling framework using deep learning with spa-
tial reduction and reconstruction, Environ. Model. Softw., 143,
105112, https://doi.org/10.1016/j.envsoft.2021.105112, 2021.

An investigation of enhanced recessions in Poyang Lake: Com-
parison of Yangtze River and local catchment impacts, J. Hydrol.,
517, 425–434, 2014.

Hydrol. Earth Syst. Sci., 29, 3833–3852, 2025
https://doi.org/10.5194/hess-29-3833-2025
