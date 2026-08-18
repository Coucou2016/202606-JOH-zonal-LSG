# Fraehr et al. (2024) Water Research 252, 121202

- **DOI:** https://doi.org/10.1016/j.watres.2024.121202
- **Local PDF:** `paper/refs/pdf/1-s2.0-S0043135424001027-main.pdf`
- **Access:** full text obtained (user-supplied publisher PDF (Elsevier open access, CC BY))
- **Conversion tool:** PyMuPDF (`fitz`) via `paper/refs/_pdf_to_md.py`
- **Pages:** 15

---

## Extracted full text (OCR-free PDF text layer)

### Page 1

Water Research 252 (2024) 121202

Contents lists available at ScienceDirect

Water Research

journal homepage: www.elsevier.com/locate/watres

Assessment of surrogate models for flood inundation: The physics-guided
LSG model vs. state-of-the-art machine learning models

Niels Fraehr *, Quan J. Wang , Wenyan Wu , Rory Nathan

Department of Infrastructure Engineering, Faculty of Engineering and Information Technology, The University of Melbourne, Victoria 3010, Australia


#### A R T I C L E I N F O



#### A B S T R A C T


Keywords:
Flood inundation
Surrogate models
Empirical orthogonal functions

#### LSTM

Gaussian process

#### CNN


Hydrodynamic models can accurately simulate flood inundation but are limited by their high computational
demand that scales non-linearly with model complexity, resolution, and domain size. Therefore, it is often not
feasible to use high-resolution hydrodynamic models for real-time flood predictions or when a large number of
predictions are needed for probabilistic flood design. Computationally efficient surrogate models have been
developed to address this issue. The recently developed Low-fidelity, Spatial analysis, and Gaussian Process
Learning (LSG) model has shown strong performance in both computational efficiency and simulation accuracy.
The LSG model is a physics-guided surrogate model that simulates flood inundation by first using an extremely
coarse and simplified (i.e. low-fidelity) hydrodynamic model to provide an initial estimate of flood inundation.
Then, the low-fidelity estimate is upskilled via Empirical Orthogonal Functions (EOF) analysis and Sparse
Gaussian Process models to provide accurate high-resolution predictions. Despite the promising results achieved
thus far, the LSG model has not been benchmarked against other surrogate models. Such a comparison is needed
to fully understand the value of the LSG model and to provide guidance for future research efforts in flood
inundation simulation. This study compares the LSG model to four state-of-the-art surrogate flood inundation
models. The surrogate models are assessed for their ability to simulate the temporal and spatial evolution of flood
inundation for events both within and beyond the range used for model training. The models are evaluated for
three distinct case studies in Australia and the United Kingdom. The LSG model is found to be superior in ac­
curacy for both flood extent and water depth, including when applied to flood events outside the range of
training data used, while achieving high computational efficiency. In addition, the low-fidelity model is found to
play a crucial role in achieving the overall superior performance of the LSG model.

1. Introduction

estimates (e.g. using Monte Carlo methods). This is due to the high
computational costs involved in running high-fidelity models for large
domains in high resolution. Researchers have explored various methods
to address this issue with high-fidelity models, including parallelisation
and high-performance computing (Neal et al., 2009; Sanders and
Schubert, 2019), efficient solution algorithms (Bates and De Roo, 2000;
Leijnse et al., 2021; Sridharan et al., 2021) and GPU processing (But­
tinger-Kreuzhuber et al., 2022; Ming et al., 2020; Morales-Hern´andez
et al., 2021). However, even with these methods high-fidelity models are
still computationally too demanding for many use cases including
real-time forecasting and ensemble modelling.

Every year flood events pose a threat to human life and cause dam­
ages worth billions of dollars (Guha-Sapir et al., 2023). To mitigate the
impacts of floods, researchers have developed hydrodynamic models to
simulate flood events and have continuously made improvements to
their performance (Bates, 2022; Teng et al., 2017). Hydrodynamic
models are physics-based models and can accurately simulate flooding
by solving complex differential equations on a high-resolution numeri­
cal grid (i.e. high-fidelity models) (Razavi et al., 2012). High-fidelity
models can accurately simulate flood events (Bates, 2022; Guo et al.,
2021; Luo et al., 2022), which makes them ideal for replicating historic
floods and in the design of new infrastructure. However, they are seldom
used for real-time forecasting or ensemble modelling where many
thousands of simulations are used to derive probabilistic design

Surrogate models have been developed to produce computationally
efficient approximations of high-fidelity models (Bentivoglio et al.,
2022; Karim et al., 2023; Mosavi et al., 2018). Surrogate models have
been applied in many research areas, including the prediction of storm

* Corresponding author.
E-mail address: n.fraehr@unimelb.edu.au (N. Fraehr).

https://doi.org/10.1016/j.watres.2024.121202
Received 16 October 2023; Received in revised form 21 January 2024; Accepted 23 January 2024

Available online 24 January 2024
0043-1354/© 2024 The Author(s). Published by Elsevier Ltd. This is an open access article under the CC BY license (http://creativecommons.org/licenses/by/4.0/).

### Page 2

N. Fraehr et al.

Water Research 252 (2024) 121202

surge and water waves (Jagtap et al., 2022; Ma et al., 2019; Malde et al.,
2016), subsurface flows (Menberg et al., 2020; Zheng et al., 2019),
reservoir modelling (Thenon et al., 2016), optimising hydrodynamic
shapes (Coppede et al., 2019), pyroclastic flow height (Gu and Berger,
2016), flood loss (Zischg et al., 2018), and lake temperature (Read et al.,
2019). In this study, we focus on the use of surrogate models for flood
inundation predictions. However, the methodologies and concepts can
readily be adapted to other research areas.

The paper is organised as follows. In Section 2, the selected surrogate
models are described. In Sections 3 and 4, the evaluation metrics and
case studies are presented, respectively. Then in Section 5, we show the
results, followed by discussions in Section 6 and finally a conclusion in
Section 7.

2. Surrogate models for comparison

Within the flood inundation modelling field, most of the surrogate
models are based on machine learning techniques, as machine learning
models have shown to be both accurate and computationally efficient (e.
g. Bermúdez et al. (2019), Chang et al. (2022), Zhou et al. (2021), Zhou
et al. (2022)), thus making them attractive for real-time forecasting and
ensemble modelling applications. Alternatively, the use of low-fidelity
surrogate models has also been explored (e.g. Bomers et al. (2019),
Jamali et al. (2019)). Low-fidelity models are simplified versions of
high-fidelity models and are thus usually less computationally efficient
than machine learning models. However because low-fidelity models are
physics-based, they often perform well at generalising for new unseen
events and extrapolation purposes (Razavi et al., 2012). A third type of
surrogate models are conceptual models that use simplified hydraulic
principles to predict flood inundation (e.g. Lhomme et al. (2008), Nobre
et al. (2016), Teng et al. (2019)). Conceptual models are computation­
ally efficient but are usually limited to predicting the maximum flood
extent, as they cannot represent dynamical inundation effects (Teng
et al., 2017).

In this section, the selection process for the surrogate models is
described followed by a brief description of each model. Complete de­
scriptions of the models can be found in the original studies cited where
the models were introduced.

2.1. Selection criteria for surrogate models

We have adopted selection criteria that are based on meeting com­
mon expectations for model performance:

• Computational speed and accuracy: The surrogate model should
have been applied to real-world case studies and proven to be ac­
curate and have high computational efficiency enabling the use of
the surrogate model in real-time forecasting and ensemble modelling
applications. This criterion excludes most low-fidelity models, such
as the SFINCS model by Leijnse et al. (2021), the cellular automata
model by Liu et al. (2015) and the RIFT model by Brent Daniel et al.
(2023), as they normally allow a lower accuracy and resolution to
achieve high computational efficiency, or are not fast enough for
real-time applications. In addition, this criterion excludes surrogate
models that have only been applied to synthetic case studies and
flood problems, as real-world problems generally provide more
challenging applications.
• Dynamic flood behaviour: Information on the dynamic progress of
a flood event can provide valuable information in emergencies. High-
fidelity models usually simulate the full dynamic evolution of flood
inundation events (Bates, 2022; Teng et al., 2017). For that reason,
surrogate models are most versatile and beneficial if they can
simulate both the spatial and temporal dynamics of the flood inun­
dation. This criterion excludes surrogate models that are limited to
predicting maximum extents and water depth only, such as the
HAND model by Nobre et al. (2016), the TVD model by Teng et al.
(2015), and the ANN models developed by Devi et al. (2019) and Lin
et al. (2020).
• Model grid structure: Modern high-fidelity models use unstruc­
tured (i.e. irregular, flexible) grids to describe complex geometries
and reduce the number of grid cells (Bates, 2022; Teng et al., 2017).
The selected surrogate models should therefore be able to emulate
high-fidelity models that use both structured and unstructured grids.
This criterion excludes two-dimensional Convolutional Neural Net­
works (2dCNN) and U-net-based surrogate models, as these can only
emulate structured grids (e.g. L¨owe et al. (2021), Mu˜noz et al.
(2021), Zhou et al. (2022)).

Recently, a physics-guided hybrid model for flood inundation
modelling, referred to as the Low-fidelity, Spatial analysis, and Gaussian
Process Learning (LSG) model, has been developed (Fraehr et al., 2022,
2023a, 2023b). The key motivation for the LSG model is to capture the
benefits of both the generalisability of a physics-based low-fidelity
model and the high computational efficiency of machine learning
models (in the case of the LSG model, a sparse Gaussian process model).
So far, the LSG model has shown strong performance with fast and ac­
curate flood inundation predictions (Fraehr et al., 2023a), but it has not
yet been compared to other promising surrogate models. Such a com­
parison is needed to understand the value of the LSG model and provide
guidance for the investigation of future flood inundation surrogate
models. Furthermore, although physics-based, -informed and/or
-guided surrogate models generally perform well (e.g. Bentivoglio et al.
(2023), He et al. (2023), Jamali et al. (2021), Read et al. (2019)), the
importance of the low-fidelity model in the LSG model setup have not
been explored. If the setup and running of the low-fidelity model can be
avoided, the LSG model would be simpler to set up and even more
computationally efficient.

In this study, we carry out a comparative study of surrogate models
intended to replace high-resolution hydrodynamic models in real-time
flood inundation forecasting and ensemble modelling applications. We
compare the LSG model against four state-of-the-art surrogate flood
inundation models, including the 1dCNN model by Kabir et al. (2020),
the LSTM-SRR model by Zhou et al. (2021), the GP-EOF model by
Donnelly et al. (2022), and the LSTM-EOF model by Hu et al. (2019).
The aim of this study is to explore the value of the LSG model as a
surrogate for flood inundation modelling, as well as to assess the
importance of including the low-fidelity model in the LSG model
structure. We use the surrogate models to simulate flood events for three
distinct case studies in Australia and the United Kingdom and evaluate
their performance by comparing them to high-fidelity reference models.
The accuracy of these surrogate models is assessed by their ability to
capture the maximum flood extent and water depth, as well as to
simulate the entire dynamic evolution of the flood inundation over time.
Furthermore, we explore the models’ ability to extrapolate and predict
events 50% larger than those used for training (i.e. extrapolated flood
events). Finally, we discuss the trade-off between accuracy and
computational efficiency for the compared models, and the future di­
rections for surrogate flood inundation models.

Using these selection criteria, we have chosen the following models
for comparison with the LSG model developed by Fraehr et al. (2023a):
the 1dCNN developed by Kabir et al. (2020), the LSTM-SRR developed
by Zhou et al. (2021), the GP-EOF model developed by Donnelly et al.
(2022) and the LSTM-EOF model developed by Hu et al. (2019). It is
worth noting that all the selected surrogate models are fully or partially
based on machine learning techniques. This is mainly due to the high
computational efficiency that can be achieved through machine learning
techniques. To the authors’ best knowledge, these models reflect the
recent trends and are state-of-the-art within the field of surrogate models
for flood inundation.

2

### Page 3

N. Fraehr et al.

Water Research 252 (2024) 121202

2.2. Selected models

flood events. The EOF analysis reduces the dimensionality of the low-
and
high-fidelity
training
datasets
by
deconstructing
the
temporal-spatial data into a linear combination of temporal and spatial
components. The key low-fidelity temporal components are used as
input to a Sparse GP model that is trained to predict the corresponding
key high-fidelity temporal components. Sparse GP models use a sparse
representation of the input data based on inducing variables, thus
making Sparse GP models computationally efficient for large training
datasets (Bauer et al., 2016; Burt et al., 2019). Individual Sparse GP
models are trained to predict each key high-fidelity temporal compo­
nent. Finally, the predicted key high-fidelity temporal components are
used to reconstruct flood inundation in high resolution and accuracy by
reversing the EOF analysis. Two LSG models are developed, one to
predict the flood extent and one to predict the water depth (noting that
both models are based on the same low-fidelity model). The flood extent
predictions are used to mask the water depth predictions resulting in one
combined prediction.

The models selected for comparison are shown in Fig. 1. All surrogate
models receive a time series of flood drivers (e.g. river flow and water
levels) as input and predict the flood inundation as output. Each sur­
rogate model needs to be trained using a dataset of inundation events.
This training dataset is commonly generated using a high-fidelity model,
as ground-truth observations of flood inundation are sparse (Bentivo­
glio et al., 2022; Karim et al., 2023). The general structure and meth­
odology behind the models are described in the following sections.

2.2.1. The LSG model (Fraehr et al., 2022, 2023a, 2023b)
The Low-fidelity, Spatial analysis, and Gaussian Process Learning
(LSG) model was originally developed to predict flood extent (Fraehr
et al., 2022), but it was later further developed to predict the water
depth as well (Fraehr et al., 2023a, 2023b). The LSG model uses a
low-fidelity model to transform time series of the flood drivers to flood
inundation patterns in time and space. The term “low-fidelity” is used
here to denote that complexity is reduced using lower spatial resolution,
longer timesteps, and simplified equations compared to the high-fidelity
models routinely used in practice. The low-fidelity model provides a
rough estimate of the flood inundation that needs to be upskilled to high
resolution and accuracy to be useful. The upskilling is performed using
Empirical Orthogonal Functions (EOF) analysis and Sparse Gaussian
Process (GP) models to establish a relationship between the low-fidelity
model and a high-fidelity model based on a training dataset of simulated

The LSG model has been tested on the flat and complex Chowilla
floodplain in Australia (740 km2), as well as the steep and coastal
catchment of the Burnett River in Australia (1,479 km2) (Fraehr et al.,
2023b). For both study sites, the LSG model has been shown able to
provide accurate prediction in a computationally efficient manner.

2.2.2. The 1dCNN model (Kabir et al., 2020)
Kabir et al. (2020) proposed the use of a one-dimensional Convolu­
tional Neural Network (1dCNN) model to predict flood inundation. The

Fig. 1. Modelling process of surrogate flood inundation models for comparison. (1) Input features are lagged in time. (2) Input features are time series sequences.
Further details on the surrogate models, how the input features are incorporated, and an explanation of abbreviations used in the figure, are given in the model
descriptions in Sections 2.2.1–2.2.5.

3

### Page 4

N. Fraehr et al.

Water Research 252 (2024) 121202

model receives flood drivers that are lagged in time from timestep t to
timestep t-m, meaning the model is given a sense of memory by incor­
porating individual input features for each of the lagged timesteps (i.e.
the model is “looking back”). The number of lagged timesteps m is based
on the specific study site and travel time of the flood inundation. This
means that the dimensionality of the inputs increases as m increases. The
model converts the input features via two 1dCNN layers, a flattening
layer, three hidden layers and an output layer to predict flood inunda­
tion for all grid cells of a high-fidelity model. The 1dCNN model has been
applied to simulate inundation in two urban catchments in the United
Kingdom by different investigators: Carlisle, 14.5 km2 (Kabir et al.,
2020); and Tadcaster, 3.6 km2 (Donnelly et al., 2022).

number of layers, the nodes in each layer etc.), and for that reason, we
choose to use the same LSTM model structure as employed by the
LSTM-SRR model. An optimised model structure could potentially
improve the results of the LSTM-EOF model, but this would involve
further model development and is considered to lie outside the scope of
direct model comparison. The LSTM-EOF model was used to simulate
flood inundation caused by a tsunami hitting Okushiri Island in Japan
(18.5 km2) and we include it in this comparison given the LSTM-EOF
model’s high similarity to the LSG and GP-EOF models.

3. Evaluation

The surrogate models chosen for the comparative analysis are
compared to high-fidelity models in their ability to predict flood extent
and water depth, as well as their computational efficiency. In the
assessment of the surrogate models’ accuracy, we only include areas that
have been flooded in the training data. This is to avoid bias of including
areas that are never inundated, and thus would easily be predicted as dry
by the surrogate models. The computational efficiency of the surrogate
models is assessed by comparing the surrogate models’ speed-up ratio (i.
e. number of times the surrogate models are faster than the high-fidelity
models) and simulation speed (i.e. number of timesteps simulated per
second wall clock time).

2.2.3. The LSTM-SRR model (Zhou et al., 2021)
The LSTM-SRR model was developed by Zhou et al. (2021) and it
combines Long Short-Term Memory (LSTM) models with a Spatial
Reduction and Reconstruction (SRR) approach to predict flood inun­
dation. The SRR approach is used to identify representative locations
that are significant for flood inundation. This facilitates the use of in­
dividual LSTM models that are trained to predict the water depth for
each of the representative locations. The LSTM models incorporate the
flood drivers as time series sequences from timestep t to timestep t-m,
thus the input dimensionality corresponds to the number of flood
drivers. The LSTM models convert the inputs via a hidden layer, a LSTM
layer and an output layer.

3.1. Evaluation metrics used for comparison

The number of LSTM models needed to be set up and trained is
reduced by predicting the water depth at representative locations
instead of all grid cells in the high-fidelity model. The predicted water
depths from the LSTM models are used to reconstruct the full inundation
surfaces via a simple two-dimensional interpolation approach. The
LSTM-SRR model was first applied to the coastal catchment of the
Burnett River in Australia (1,479 km2) (Zhou et al., 2021), but was later
used to simulate flooding at the King River-Ovens River system in
Australia (391 km2) (Zhou et al., 2022).

3.1.1. Flood extent
The flood extent is an important parameter when evaluating flood
inundation models because an accurate understanding of flood extent
can help allocate resources to vulnerable areas in emergencies. The flood
extent is evaluated using the Critical Success Index (CSI) (See Eq. (1)),
which is a comprehensive index to assess both the False Alarm Rate and
Probability Of Detection (Schaefer, 1990).


#### CSI =

TP

#### TP + FN + FP

(1)

2.2.4. The GP-EOF model (Donnelly et al., 2022)
Donnelly et al. (2022) showed that GP models can effectively
simulate flood inundation by first predicting the key high-fidelity tem­
poral components from EOF analysis and then subsequently by reversing
the EOF analysis to reconstruct the inundation surfaces. This approach is
analogous to the LSG model described in Section 2.2.1, but instead of
using a low-fidelity model to transform the flood drivers in time and
space, the GP-EOF model predicts the key high-fidelity temporal com­
ponents directly from the flood drivers. The flood drivers are lagged in
time, similarly to the approach described for the 1dCNN model in Sec­
tion 2.2.2.

True Positive (TP) denotes those cells correctly predicted as flooded,
False Negative (FN) relates to those cells predicted as dry using the
surrogate model but which are flooded using the high-fidelity model,
and False Positive (FP) represents those cells predicted as flooded using
the surrogate model but which are dry using the high-fidelity model. The
CSI can take values between 0 and 1, where a CSI of 1 is considered a
perfect prediction.

3.1.2. Peak water depth
The peak water depth is commonly used for evaluating model per­
formance and is a common indicator of the severity of a flood event. The
surrogate models’ ability to predict the peak water depth is assessed
using the Average Peak Difference (AvgPeakDiff, see Eq. (2)) and the
coefficient of determination (R2, see Eq. (3)) (Wright, 1921).

To the authors’ knowledge, the GP-EOF model has only been applied
to the urban catchment of Tadcaster (3.6 km2) in the UK (Donnelly et al.,
2022). The model was selected for comparison because it represents an
alternative application of EOF analysis without relying on a low-fidelity
model. That is, it provides a fully independent means of evaluating the
benefit of combining the low-fidelity model with EOF analysis, as used
by the LSG model. We set up the GP-EOF model equally to the LSG
model, using Sparse GP models with exponential kernel-covariance
functions (Tests showed minimal difference in the results compared to
using full GP models with a Matern 3/2 kernel as in the original study)
and two separate models to predict the flood extent and water depth.
The only difference between the LSG and GP-EOF models is thus
whether to include or not include the low-fidelity model.

∑
N

AvgPeakDiff = 1

ymax(n) −̂ ymax(n)
(2)

N

n=1

∑N

n=1(ymax(n) −̂ ymax(n))2
∑N


#### R2 = 1 −


n=1(ymax(n) −ymax)2
(3)

where ymax and ̂ymax is the peak water depth for the high-fidelity and
surrogate models, ymax is the mean peak value of the high-fidelity model,
and N is the total number of cells. An AvgPeakDiff of 0 and a R2 of 1 are
considered perfect predictions.

2.2.5. The LSTM-EOF (Hu et al., 2019)
The LSTM-EOF model was developed by Hu et al. (2019) and uses the
same concept as the GP-EOF model. The only difference is that an LSTM
model was used instead of a GP model to predict the key high-fidelity
temporal components from the EOF analysis. Unfortunately, Hu et al.
(2019) do not fully describe the structure of their LSTM model (i.e. the

3.1.3. Water depth hydrographs
Flood events evolve over time and it is thus desirable for a flood
inundation model to capture the dynamic evolution of the water depths
in space and time. The ability of a surrogate model to capture dynamic

4

### Page 5

N. Fraehr et al.

Water Research 252 (2024) 121202

inundation behaviour is evaluated using the average Root Mean Square
Error (AvgRMSE, see Eq. (4)) and the Fidelity Index (FI, see Eq. (5)). The
FI is a simple metric to determine how often a surrogate model predicts
the water depth within a tolerance window (Fraehr et al., 2023b). The
tolerance window consists of a water depth tolerance of +/- 5 cm and a
timing tolerance of +/- 5% of the event duration. The tolerance window
allows for minor errors that are considered insignificant compared to the
general surrogate model performance.

et al., 2023; Sit et al., 2020). That is, while it might be expected that
better model performance could be achieved through optimisation to
site-specific conditions, we consider application of the models as pub­
lished represents a reasonable basis to assess their general applicability
by users who are independent of the developers.

Before training, all input and outputs for the LSG, GP-EOF, and
LSTM-EOF models were standardised to zero mean and unit variance.
Following Kabir et al. (2020), only the inputs are standardised for the
1dCNN model. For the LSTM-SRR model, all input flows are normalised
based on the maximum flow rate and downstream water levels are
normalised to values between 0 and 1 (Zhou et al., 2021). After training,
all surrogate models are evaluated by comparing them to high-fidelity
simulations.

√
√
√
√
(4)

∑
N

∑
T

AvgRMSE = 1

1
T

(̂y(t, n) −y(t, n))2

N

n=1̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅

t=1

{

∑
T

∑
N


#### FI =

1

#### T⋅N⋅


1, min{|̂y(t, n) −y(t−Δt : t+Δt, n)|} ≤Δh
0, min{|̂y(t, n) −y(t−Δt : t+Δt, n)|} > Δh
(5)

4. Case studies

t=1

n=1

where y and ̂y are the water depths predicted for each cell by the high-
fidelity and surrogate models respectively, t−Δt and t+Δt are the time t
+/- the time threshold Δt, Δh is the water depth threshold, and T is the
total number of timesteps. An AvgRMSE of 0 and a FI of 1 is considered a
perfect prediction.

We evaluate the surrogate model on three case studies; Carlisle in the
United Kingdom, the Chowilla floodplain in Australia, and the Burnett
River in Australia. Table 1 and Fig. 2 provide an overview of the case
studies and their general characteristics. The case studies are described
in the following sections.

3.2. Training and validation

4.1. Carlisle

We generate datasets for training and validation of the surrogate
models using a high-fidelity model to simulate a selection of flood
events. For the LSG model, these flood events also need to be simulated
using a low-fidelity model to create a low-fidelity model dataset for
training and validation. The details of the low-fidelity model develop­
ment are described in Fraehr et al. (2023b). The low- and high-fidelity
models are forced using input hydrographs. The datasets must include
a wide range of flooding behaviour to ensure a good performance of the
surrogate models for new flood events. In this study, the datasets are
generated by simulating flood events using input hydrographs and
high-fidelity models developed in previous studies (See Section 4). In
these previous studies, some of the flood events were developed by
simply scaling input hydrographs to different magnitudes and simu­
lating them using the high-fidelity model. This means the datasets
consist of groups of events that share similar temporal patterns (i.e.
shape of hydrograph). It is not desirable to include events with similar
temporal patterns in both training and validation datasets, as we aim to
explore the generalisability of the surrogate models for new unseen
events. To avoid this, we choose to use leave-one-out cross-validation on
the groups of flood events. For each fold in the cross-validation, we use
one group for validation and the remaining for training. Additional in­
formation on the input hydrographs, high-fidelity simulation results (i.e.
the datasets used for training and validation), and the groups used in the
cross-validation can be found in the data repository released with this
study Fraehr (2024).

The Carlisle case study has previously been used in several studies (e.
g. (Neal et al., 2013, Parkes et al., 2013)), as well as for the development
of the 1dCNN model (Kabir et al., 2020). Carlisle is a city in Northwest
England with three main rivers flowing through. Carlisle has a flat
topography, which makes it prone to flooding when the river capacities
are exceeded.

Flooding is simulated using a high-fidelity model developed using
LISFLOOD-FP modelling software (Bates and De Roo, 2000). The
high-fidelity model simulates flooding using a structured quadratic grid
with a resolution of 5 m x 5 m and a Manning’s n of 0.055 s/m1/3. Flood
events are simulated using the time series of boundary inflows obtained
from (Kabir et al., 2020). The water level at the outlet is calculated in
LISFLOOD-FP using a normal depth condition. Results are available at

#### 15 min intervals. The low-fidelity model used for the LSG model was

developed using HEC-RAS modelling software (US Army Corps of En­
gineers, 2021) and has an unstructured grid with 5,681 cells varying in
size between 1193 and 4341 m2. The low-fidelity model uses the same
boundary and roughness conditions as the high-fidelity model.

4.2. Chowilla floodplain

The Chowilla floodplain has a flat topography with several anab­
ranches and has previously been used by Fraehr et al. (2023a) and
Fraehr et al. (2023b) in the development of the LSG model. The Chowilla
floodplain is part of the Murray-Darling basin and is located in Australia
on the border between Victoria, New South Wales and South Australia.

All the surrogate models are programmed in Python using Tensor­
flow (Abadi et al., 2016) and GPflow (Matthews et al., 2017). The
training datasets are split randomly into training (90%) and testing
(10%), and all surrogate models are trained and tested using identical
splits of the data. We train the 1dCNN, LSTM-SRR and LSTM-EOF
models using the ADAM optimiser (Diederik and Ba, 2017) with a
mean squared error loss function. The two GP-based surrogate models
(the LSG and GP-EOF models) are trained using the L-BFGS-B algorithm
(Zhu et al., 1997) to perform maximum likelihood optimisation. The
testing set is used for early stopping and in initial tests for optimising
hyperparameters (e.g. learning rate, batch size). We chose not to opti­
mise the surrogate model structure (e.g. number of layers, nodes in each
layer, activation functions, number of inducing variables in GP models
etc.) as we wish to evaluate the performance of the models as they would
be applied by users, not developers. This decision was taken as surrogate
models should be easy to set up and use and often even researchers do
not fully understand the intuition required for their development (Maier

Table 1
Overview of case studies and general characteristics.

Carlisle
Chowilla
Burnett River

Model domain size

#### 14.5 km2


#### 740 km2

1,479 km2

Number of inflows
3
3
14
Range of inflows (Min-Max)

#### 0 – 1950

m3/s


#### 0 – 1184 m3/s


#### 0 – 18509

m3/s
Duration of flood events
Hours to
Days

Weeks to
months

Days to weeks

Travel time through the domain

#### 2 h


#### 10 days


#### 48 h

High-fidelity model
581,061
cells

109,914 cells
3,697,597
cells
Total simulated flood events
9
29
74
Groups based on different

9
10
4

temporal patterns

Timestep of flood results

#### 15 min


#### 8 h


#### 1 h


5

### Page 6

N. Fraehr et al.

Water Research 252 (2024) 121202

Fig. 2. Overview of case studies. Panels a and b show the location of the study sites in Australia and the United Kingdom. Panel c, d, and e show the model domains
and elevation for the Chowilla floodplain, Carlisle, and Burnett River, respectively. Basemaps are from OpenStreetMap (2023).

The flow is regulated using 22 weirs and control structures which results
in a complex exchange of flows between the main channel and the
floodplain. The floodplain receives water from three main rivers that
converge into one within the floodplain.

of the surrogate models it is important to include extreme events in the
training data, so the surrogate models can predict flooding for new
events that are possibly larger than historic records. This is further
explored in Section 5.5.

The available high-fidelity model is developed using HEC-RAS. The
high-fidelity model simulates flooding using an unstructured grid with
varying grid cell sizes between 139 and 25,628 m2 with a Manning’s n of

#### 0.026 s/m1/3 in the rivers and 0.083 s/m1/3 on the floodplain. The high-

fidelity model is forced by three inflow boundary conditions and one
outlet water level boundary condition. Time series data is available for
all boundary conditions, and results are saved at 6 hourly timestep in­
tervals. The LSG model incorporates a low-fidelity model that is set up
using HEC-RAS. The low-fidelity model has 1,434 cells in an unstruc­
tured grid ranging in size from 1,172 to 9,337,095 m2 (Fraehr et al.,
2023b).

The 1dCNN model was only applied and compared for every 4th grid
cell in the Burnett River case study as computational constraints pre­
vented storage of the entire high-fidelity dataset in memory during
training. The 1dCNN model was trained on all grid cells and fully
comparable for the Carlisle and Chowilla floodplain case studies, and the
choice of training on fewer grid cells in the Burnett River is thus assumed
to have limited impact on the general conclusions for the 1dCNN model.

The number of lagged timesteps or sequence lengths used as input for
the 1dCNN, LSTM-SRR, GP-EOF, and LSTM-EOF models correspond to
the travel time through the domain in Table 1. For example, the Carlisle
case study has three inflows, a two-hour travel time, and 15 min time­
steps. This means the 1dCNN and GP-EOF models receive 27 input
features, corresponding to the current timestep for all three inflows, plus

#### 3 inflows for each of the previous 8 timesteps. In contrast, the LSTM-SRR

and LSTM-EOF models receive three input sequences that are two hours
long. The input features to the sparse GP model in the LSG model are the
key temporal components derived from EOF analysis of the low-fidelity
data (See Section 2.2.1), typically between 3 and 15 features depending
on the training data. The low-fidelity model in the LSG model handles
the temporal aspects of the LSG model’s flood predictions, thus the input
features to the GP model in the LSG model do not have to be lagged in
time unless the temporal evolution of the low-fidelity estimate is
significantly different from the high-fidelity model.

4.3. Burnett River

The Burnett River drains steep topography resulting in fast-flowing
water. The Burnett River is located downstream of Paradise Dam in
Queensland, Australia and was originally used as a case study by Zhou
et al. (2021) for the development of the LSTM-SRR model, but has later
also been used in Fraehr et al. (2023b).

The high-fidelity model was developed using TUFLOW modelling
software (Huxley and Syme, 2016). Flooding is simulated using a 20 m x

#### 20 m quadratic grid and Manning’s n varying from 0.02 s/m1/3 to 0.15

s/m1/3. The high-fidelity model receives water from 14 inflow bound­
aries, and the water level downstream is controlled by the sea water
level at Burnett Heads. The high-fidelity results are available at 1 h in­
tervals. The corresponding low-fidelity model used in the LSG model is
developed in HEC-RAS. The low-fidelity model simulates flooding using
an unstructured grid with 15,256 cells with sizes ranging from 194 to
547,124 m2.

5. Results

5.1. Flood extent

The surrogate model results for simulating flood extents for all case
studies are shown in Fig. 3. It is seen that the LSG and LSTM-EOF models
perform consistently well across all case studies and that the other
models exhibit more variable performances. All models generally cap­
ture well the maximum flood extent for the Carlisle case study. This is
indicated by a median CSI above 0.75 for all models (See Fig. 3). For the
Chowilla floodplain, the LSTM-SRR model shows reduced accuracy with
CSI values below 0.5. The Chowilla floodplain has a flat topography with
many anabranches. This type of topography is similar to the King River-
Ovens River system used in Zhou et al. (2022), where the LSTM-SRR

4.4. Application of the surrogate models to case studies

In the setup and application of the surrogate models, we only include
cells that are flooded during the training events. This reduces the size of
the training datasets by excluding areas that are never inundated (i.e.,
dry cells). Including dry areas in the training data would merely add
noise to the data, as the surrogate models would have no information
about when these areas would get inundated. To ensure the performance

6

### Page 7

N. Fraehr et al.

Water Research 252 (2024) 121202

Fig. 3. Critical success index for the maximum flood extent predicted using surrogate models. A CSI of 1 indicates a perfect prediction.

model also showed reduced accuracy, thus indicating the LSTM-SRR
model may not perform well for this type of case study. The GP-EOF
and 1dCNN show reduced accuracy in the Burnett River case study.
This is most likely due to the use of lagged input features in these two
models that retain information over the previous 48 h at 14 inflow lo­
cations at 1 h timesteps (see model descriptions in Section 2.2 and
Table 1). This means the GP-EOF and 1dCNN models receive 720 input
features, which represents a high degree of dimensionality that makes it
difficult to optimise the models.

model also incorporates EOF analysis and uses separate models for the
extent and water depth but has reduced accuracy for the Burnett River
case study due to the use of lagged input features resulting in a high
input dimensionality as previously described.

5.2. Peak water depth

The LSG model yields the smallest average difference in peak levels
compared to the other models for all case studies (Fig. 4), with values
closely located around 0 m, indicating no general bias for over- or
underprediction. The 1dCNN model also shows a good ability to capture
the peak although with a lower degree of accuracy than the LSG model
in the Carlisle and Burnett River case studies. The LSTM-SRR model
exhibits the lowest accuracy in peak water depth for the Carlisle and
Chowilla floodplain case studies, while the GP-EOF model has the lowest
accuracy in the Burnett River.

The LSG model captures the extent the best of all the surrogate
models with high CSI values for all case studies. After the LSG model, the
LSTM-EOF model has the highest CSI values. This suggests that the use of
EOF analysis, which is incorporated in both the LSG and LSTM-EOF
models, is a method that reliably captures the flood extent. Another
reason that the LSG and LSTM-EOF models predict the flood extents well
could be that they simulate the flood extent and depths separately using
two separate models, while the LSTM-SRR and 1dCNN models predict
the water depth only and derive the extent from the water depth pre­
dictions. Fraehr et al. (2023a) showed that using separate LSG models to
predict the depth and extent of flooding results in higher accuracy than
deriving the flood extent from water depth predictions alone. The results
of this earlier study together with the results of this study suggest that
using separate models for flood extent and water depth could also pro­
vide improved accuracy for other surrogate models than the LSG model,
although this may also increase training and prediction time if the extent
and water depth models are not run in parallel. Note, that the GP-EOF

The LSG, 1dCNN, GP-EOF and LSTM-EOF models show high accu­
racy for the peak water depth in the Chowilla floodplain. This is most
likely due to the Chowilla floodplain’s flat topography and slow-moving
water that results in shallow gradients and small water depth differences
across the floodplain, which makes the peak level easier to predict. In
addition, more training events are available for the Chowilla floodplain
compared to the Carlisle case study (See Table 1), and this assists the
ability of the surrogate models to provide more robust predictions for
new events in the Chowilla floodplain.

The results for the coefficient of determination (R2) for peak water

Fig. 4. Difference in peak water depth predictions between the high-fidelity model and surrogate models. Negative values indicate overprediction of the peak
compared to the high-fidelity model. An average peak difference of 0 indicates a perfect prediction.

7

### Page 8

N. Fraehr et al.

Water Research 252 (2024) 121202

depth predictions (Fig. 5) show the same trends as seen for the average
peak difference. The LSG model shows the best accuracy with R2 values
close to 1 for all simulated events thus confirming its good ability to
capture the peak water depth. The 1dCNN and LSTM-EOF models also
generally show high R2 values.

grid cells. It is to be noted that this assessment of computational effi­
ciency does not consider the time required to set up and train the sur­
rogate models as this only has to be done once, and thereafter the
surrogate models can be used for flood prediction.

5.5. Performance over extrapolated events beyond training data

5.3. Water depth hydrographs

Flood events increase in size due to climate change (IPCC, 2021). For
this reason, it is important to examine how well the surrogate models
perform for new flood events that are larger than the ones used for
training. We explore the surrogate models’ ability to make predictions
outside the training data (i.e., extrapolation) by simulating a new flood
event arising from inflows that are 50% larger than used in the original
training data. We predict one larger event for each case study. It should
be noted that in practice, large synthetic flood events should always be
included in the training data. The surrogate models are trained using
high-fidelity model results, and flood events of various sizes can there­
fore easily be generated by running the high-fidelity model (which of
course involves some initial computational costs in the surrogate model
development). This section thus serves as a theoretical study in the case
where such large events have not been included in the training data.

The ability of the surrogate models to capture the dynamic evolution
of the flood event is evaluated using the RMSE and FI metrics in Fig. 6
and Fig. 7, respectively. It is seen that the LSG model performs consis­
tently well across all three case studies, as shown by RMSE values below

#### 25 cm and FI above 80 %. This means the LSG model can be expected to

perform well throughout flood events in addition to its ability to capture
the flood extent or peak. This is especially obvious in the Carlisle case
study, where the LSG model shows FI values around 80-90 %, whereas
the other surrogate models have FI values in the range of 60-80 %.

The LSTM-EOF model shows the second-best performance followed
by the 1dCNN model. The results for the GP-EOF and LSTM-SRR models
vary from case study to case study. This means, the performance of the
GP-EOF and LSTM-SRR models is highly dependent on the case studies,
to which they are applied. The results are consistent with the previous
sections for the flood extent and peak water depth.

The surrogate models are all trained to predict flooding in areas that
have previously been flooded during the training events. This means
that new areas cannot be flooded unless larger events are included in the
training data. To explore the importance of having large events in the
training data, we perform a test where we include one new event for
training and retrain the models. The new flood event is 100% larger than
the original training data and thus allows the surrogate models to be
trained on a wider range of flooding behaviour.

5.4. Computational efficiency

The speed-up ratio of the surrogate models’ flood predictions
compared to the high-fidelity models varies between the case studies
(See Fig. 8). This is due to the difference in the number of grid cells,
duration of flood events, and high-fidelity model software used. All the
surrogate models show speed-up ratios of approximately 100 times or
more compared to the high-fidelity models. The 1dCNN model shows
the highest computational efficiency for all three case studies, with
speed-up ratios more than 100,000 times faster than the high-fidelity
models in the Chowilla floodplain and Burnett River. The 1dCNN
model could therefore be a good choice for probabilistic design floods
using Monte Carlo methods (or similar), but given the reduced accuracy
of the 1dCNN model shown in the previous section, the choice of model
should be considered carefully. The GP-EOF model shows the second-
highest speed-up ratio, followed by the LSG and LSTM-EOF models,
while the LSTM-SRR is the slowest of the surrogate models used in this
study.

Fig. 10 shows the accuracy of the surrogate models. Values are
shown for the case where surrogate models are trained using the original
training data (“Original training”) and also for the case where the sur­
rogate models have been retrained to include a new flood event that is
100% larger than the original training events (“New training”). The
performances are worse for the extrapolation tests compared to the
previous sections where the predicted flood events were within the
range of conditions used for training. However, once a new training
event is included, all surrogate models’ performances are improved,
despite this event being significantly larger than the original training
data and the 50% event used for prediction. This result highlights the
importance of including large (possibly synthetic) events in the datasets
used to train the surrogate models. However, although the retraining
improves the accuracy, the accuracy of all models is still lower than the
results obtained when the training data provides good coverage of the
inundation behaviour (See Section 5.1–5.3).

The simulation speed in Fig. 9 shows the same trends as the speed-up
ratio when comparing the surrogate models to each other. When
comparing across the case studies, the simulation speed is generally the
lowest for the Burnett River, because the Burnett River contains the most

To gain further insight into the reduced accuracy seen for the

Fig. 5. Coefficient of determination for peak water depth predictions between the high-fidelity model and surrogate models. A R2 of 1 indicates a perfect prediction.

8

### Page 9

N. Fraehr et al.

Water Research 252 (2024) 121202

Fig. 6. Average RMSE for water depth hydrograph predictions between the high-fidelity model and surrogate models. An average RMSE of 0 indicates a per­
fect prediction.

Fig. 7. Fidelity index for water depth hydrograph predictions between the high-fidelity model and surrogate models. A FI of 1 indicates a perfect prediction.

Fig. 8. Speed-up ratio of the surrogate models compared to the high-fidelity model.

extrapolation events, we show the maximum water depth in Fig. 11
simulated using the high-fidelity model, the LSG model trained on the
original training data, and the LSG model trained on the new training
data. We only consider the LSG model, as this has shown the best

accuracy of all the surrogate models.

In the Carlisle case study, it is evident that the model domain is too
small for the 50% larger flood event. This is seen by the flood water
accumulating along the model boundaries edges and not leaving the

9

### Page 10

N. Fraehr et al.

Water Research 252 (2024) 121202

Fig. 9. Number of simulated timesteps per second using the surrogate models.

Fig. 10. The accuracy of the surrogate models for simulating a flood event that is 50% larger than the events included in the original training. The dashed line
indicates a perfect prediction for each of the accuracy evaluation metrics.

model domain, especially in the northeastern corner (i.e. the water
follows the straight lines of the model boundaries). The LSG model
trained on the original training data cannot capture the full extent and
depths of inundation as a smaller area of the model domain was inun­
dated in the original training data. However, the performance of the LSG
model is improved in the Carlisle application once the 100% larger flood
is included in the training data.

training data is needed to ensure good surrogate model performance.

5.6. Summary of general performance across all case studies

The results of the model comparison based on all case studies are
summarised in Table 2. These results provide an indication of the ex­
pected accuracy for each model if applied to a new case study. We have
not included the results from the extrapolation tests in Section 5.5,
because the surrogate models should always be applied with training
data that covers the possible inundation behaviour. The absolute metrics
for computational efficiency are highly dependent on the case study and
high-fidelity model used. This is evident from the large standard de­
viations for the speed-up ratio and simulation speed. The LSG model
shows the best performance for all accuracy metrics used, whereas the
1dCNN model is the fastest surrogate model.

In the Chowilla floodplain and Burnett River applications, the trend
of improved performance after retraining the LSG model is also evident.
This is particularly evident in the Burnett River, where the LSG model
trained on the original data falsely predicts the northeastern part of the
study area to be mostly dry, whereas the LSG model trained with new
training data correctly predicts this area as inundated. However, the LSG
model with new training data still underpredicts the water depths in the
Chowilla floodplain and overpredicts the water depths in the Burnett
River compared to the high-fidelity model. This suggests that additional

10

### Page 11

N. Fraehr et al.

Water Research 252 (2024) 121202

Fig. 11. Maximum water depth using the high-fidelity model, the LSG model with no retraining and the retrained LSG model. Basemaps from OpenStreetMap (2023).

6. Discussion

configuration changes.

The surrogate model structures (e.g. number of layers, nodes in each
layer, covariance function) were not optimised in this study (See Section
3.2). This was done deliberately to explore how well the models would
perform for new applications with minimum effort from the model user.
Better performance could potentially be achieved by modifying model
structures. However, the 1dCNN model structure was originally devel­
oped for the Carlisle case study, and the LSTM-SRR model structure was
developed for the Burnett River case study. The LSG outperforms the
1dCNN and LSTM-SRR in these two case studies, and for that reason, we
do not believe modifying the surrogate models’ structures would change
the conclusions.

From the results shown in Section 5, it is clear that the LSG model
outperforms the other machine learning-based surrogate models across
all case studies in terms of accuracy. Each case study provides a different
challenge for the surrogate models. The Carlisle case study has the
smallest amount of training data available, is located in an urban envi­
ronment, and covers the smallest area; the Chowilla floodplain is in a
rural area, has many anabranches and several structures that affect the
flow patterns; and the Burnett River has fast flowing water and covers
the largest area (with the largest number of grid cells). Furthermore, a
different high-fidelity model (i.e. different software and resolution) is
used for each case study: the LISFLOOD-FP, HEC-RAS and TUFLOW
models are used for the Carlisle, Chowilla floodplain, and Burnett River,
respectively. The fact that the LSG model consistently provides accurate
results across case studies shows the robustness of the LSG model under

When modelling flood events with inflows much larger than the ones
used for training (i.e. extrapolation), neither of the surrogate models
investigated in this study performs particularly well. The surrogate
models are trained to predict flooding based on data from previous

11

### Page 12

N. Fraehr et al.

Water Research 252 (2024) 121202

reasons. Setting up the LSTM-SRR model requires a general under­
standing of machine learning models and their hyperparameters, and in
addition, it is necessary to prepare several input files for the maximum
extent and digital elevation surface; both of which need to be masked to
define downstream boundaries and permanent water bodies. Further­
more, input parameters to the SRR module need to be calibrated to
control the number of representative locations selected by the module.
In contrast, the LSG model requires less expertise in machine learning,
but it does require some statistical understanding of EOF analysis and
experience in using hydrodynamic models to set up the low-fidelity
model. The latter may make the LSG model easier to set up for the
general flood modeller as it would be expected that they have expertise
within hydrodynamic modelling rather than within the use of machine
learning models (Maier et al., 2023; Sit et al., 2020). The 1dCNN model
was the easiest of the surrogate models to set up, although it still re­
quires experience using machine learning models. The LSTM-EOF and
GP-EOF models are fairly similar and require machine learning and EOF
analysis experience to set up.

Table 2
Evaluation metrics for surrogate model comparison. Values are mean values
with standard deviation shown in parentheses. The best performance for each
metric is shown in bold.

Surrogate model

#### LSG

1dCNN

#### LSTM-


#### SRR



#### GP-EOF


#### LSTM-


#### EOF



#### CSI [-]

0.95
(0.05)

0.93
(0.07)
AvgPeakDiff [m]
0.00
(0.08)


#### 0.75 (0.20)

0.75
(0.19)

0.68
(0.22)

0.04
(0.13)

#### R2 [-]

1.00
(0.00)

-0.11
(0.29)

0.39
(0.73)

1.19
(1.41)

0.99
(0.03)
AvgRMSE [m]
0.18
(0.09)


#### 0.98 (0.02)

0.76
(0.32)

0.67
(0.36)

0.29
(0.19)

#### FI [-]

0.91
(0.04)


#### 0.27 (0.20)

0.91
(0.65)

1.11
(1.01)

0.88
(0.07)
Speed-up ratio


#### 0.85 (0.08)

0.66
(0.19)

0.76
(0.13)

2392
(1469)
Sim. speed

2980
(1954)

178755
(82381)

1503
(1123)

7922
(4773)

[-]


#### 12 (3)


#### 767 (448)


#### 6 (3)


#### 43 (39)


#### 11 (8)


[timesteps/s]

All the surrogate models used in this comparison need to be trained
to provide useful results. Training of the surrogate models is an opti­
misation problem, where this study aims to optimise the models to
emulate the results of high-fidelity models. From the authors’ experi­
ence, the LSTM-SRR, LSTM-EOF and 1dCNN models require the longest
computational time to find a good solution. This is due to the complexity
of these models, resulting in a large number of weights needed to be
optimised. The LSG and GP-EOF need less time to optimise to a good
solution as GP models have fewer parameters to optimise, and can be
optimised using maximum likelihood optimisation.

simulated flood events, thus it is understandable they do not predict
flooding in areas that have never been flooded in the training data. For
this reason, it is important to include a wide range of flooding behaviour
in the training data, including large flood events (e.g. Probable
Maximum Flood events) to ensure the surrogate models have flood in­
formation for all areas of the model domain. In practice, this is easily
done by running the high-fidelity model to generate the needed training
data.

All the surrogate models show a high computational efficiency
compared to the high-fidelity models, whereas the 1dCNN model was
found to be the most computationally efficient. The smallest gain in
computational efficiency by using any of the surrogate models is seen in
the Carlisle case study. This is because the high-fidelity LISFLOOD-FP
model used in the Carlisle case study is already a fast hydrodynamic
model for flood inundation (Bates and De Roo, 2000) and the flood
events in Carlisle are relatively short, thus only moderate speed-ups can
be achieved in this case study. All the surrogate models show speed-up
ratios of over 100 times compared to the high-fidelity models and can
simulate flood events lasting hours to weeks in less than a minute. We
consider all models fast enough for real-time forecasting and can be used
for running large ensembles of simulations within a reasonable
timeframe.

One of the main purposes of this study was to explore the importance
of using the physics-based low-fidelity model to guide the sparse
Gaussian process model in the LSG model setup. Comparing the LSG and
GP-EOF models, it is clear that the incorporation of the low-fidelity
model significantly improves prediction accuracy. The low-fidelity
model transforms the boundary inputs to low-resolution estimates of
the flood inundation in time and space. These estimates may have large
errors as a result of fluctuations and overestimations (for example see
Fig. 6 in Fraehr et al. (2023a) and Fig. 4 in Fraehr et al. (2023b)), but the
low-fidelity model still has the ability to capture the main flood patterns.
This ability makes it intrinsically easier to use the GP model in the LSG
model to convert low-resolution flood estimates to high-resolution flood
predictions, rather than to convert boundary inputs directly to
high-resolution flood predictions as in the case of the GP-EOF model. In
addition, the low-fidelity model is physics-based and thus can incorpo­
rate hysteresis and handle the temporal aspects of the flood predictions.
This reduces the need for the input features to the GP model within the
LSG model to be lagged in time to incorporate prior information. In the
GP-EOF model, the input boundary conditions are lagged in time. This is
a simple approach to provide the GP model with information from
previous timesteps. However, when there is a large number of input
boundary conditions and/or many lagged timesteps that need to be
included, this approach results in high dimensional input features that
can hinder the training of the GP model due to the curse of dimen­
sionality (See results for the Burnett River case study in Section 5). To
avoid this issue of using lagged inputs, more sophisticated machine
learning models, like the LSTM model that can incorporate sequential
data, can be used. Replacing the GP model with a LSTM model does
improve the accuracy of the predictions, as seen by the LSTM-EOF model
compared to the GP-EOF model. However, the LSTM-EOF model does
not outperform the LSG model. This shows that even when a sophisti­
cated machine learning model is used, it cannot compensate for the
physics-guided information provided by the low-fidelity model.

When considering the use of a surrogate model, the setup of the
model needs to be as easy as possible. A model that is complex to set up
increases the likelihood of configuration errors and potentially offers a
poor return on effort compared to simpler models, and thus will not be
attractive to users unless there are compelling advantages in terms of
speed and/or accuracy. Table 3 provides a relative comparison of the
surrogate models based on the authors’ experience in setting up and
training the surrogate models in this study. We found the LSTM-SRR and
LSG models to be the most complex to set up, although for different

Table 3
Relative comparison of the surrogate models based on the authors’ experience
setting up, training, and applying the surrogate models. The models are given a
score of low to high for qualitative metrics and are ranked from best (1) to worst
(5) for quantitative metrics.

Surrogate model

#### LSG

1dCNN

#### LSTM-


#### SRR



#### GP-EOF


#### LSTM-


#### EOF


Machine learning

Medium
Medium
High
Medium
High

skills

EOF analysis skills
Medium
Low
Low
Medium
Low
Hydrodynamic

In this study, we have chosen to limit the comparison to a selection of
surrogate models that can emulate high-fidelity models with unstruc­
tured grids and predict the temporal-spatial evolution of flood inunda­
tion. Recent literature suggests that Graph Neural Networks (GNN) and
2dCNN-based
surrogate
models
provide
promising
modelling

High
Medium
Medium
Medium
Medium

modelling skills

Training effort
Low
Medium
High
Low
High
Accuracy
1
3
4
5
2
Speed-up ratio
3
1
5
2
4

12

### Page 13

N. Fraehr et al.

Water Research 252 (2024) 121202

approaches for flood inundation modelling (Bentivoglio et al., 2022;
Chitwatkulsiri and Miyamoto, 2023; Karim et al., 2023). GNNs can
incorporate geometric features, making it possible to use GNNs to
emulate the geometry of a high-fidelity model’s computational grid.
However, the use of GNNs for flood inundation modelling is still in its
infancy, and so far GNNs have only been applied in a few use cases and
for synthetic case studies (e.g. Bentivoglio et al. (2023)). 2dCNN sur­
rogate models (e.g. Hou et al. (2021), Mu˜noz et al. (2021)) including the
advanced versions of 2dCNNs named Generative Adversarial Networks
(GAN) and U-net (e.g. do Lago et al. (2023), L¨owe et al. (2021), Zhou
et al. (2022)) have been used for several flood studies. Modern
high-fidelity models use unstructured grids (Bates, 2022), but 2dCNN
models were originally developed for processing raster data (i.e. struc­
tured grid) (Bentivoglio et al., 2022). This means that to use a
2dCNN-based surrogate model to emulate a high-fidelity model with an
unstructured grid, the training data needs to be interpolated to the
highest resolution in the high-fidelity grid. This will ensure all infor­
mation from the high-fidelity model can be used for training but will
increase the data storage needed, can be time-consuming, and interpo­
lation errors will affect the accuracy of the surrogate model. For this
reason, 2dCNN models are not considered in this study.

to ensure good accuracy of the surrogate models.

The surrogate models chosen for the comparison with the LSG model
were selected based on their ability to provide fast and accurate pre­
dictions for real-world flood problems, predict the dynamic evolution of
flood inundation, and whether they can emulate high-fidelity models
with unstructured grids. Surrogate modelling for flood inundation is an
active area of research. For that reason, we encourage others to use data
from our case studies and compare the results shown in this paper.
Comparing models using the same training data and case studies ensures
transparency of the model performance and will help progress the
development of future flood inundation models.

Open research

The surrogate models are all developed using Python (Version 3.9)
and are available from the data repository in Fraehr (2024) together
with the high- and low-fidelity model results.

CRediT authorship contribution statement

Niels Fraehr: Conceptualization, Data curation, Formal analysis,
Investigation, Methodology, Software, Validation, Visualization,
Writing – original draft, Writing – review & editing. Quan J. Wang:
Conceptualization, Project administration, Supervision, Writing – orig­
inal draft, Writing – review & editing, Resources. Wenyan Wu: Re­
sources, Supervision, Writing – original draft, Writing – review &
editing, Conceptualization. Rory Nathan: Conceptualization, Supervi­
sion, Writing – original draft, Writing – review & editing.

The field of surrogate modelling for flood inundation is an active area
of research, and new models are continuously developed. However, the
comparison of new models using the same training data and case studies
is not straightforward, as there is a lack of publicly available datasets in
the water field (Karim et al., 2023; Sit et al., 2020). For this purpose, we
have made the code and high-fidelity model simulation results used in
this study available at the data repository https://doi.org/10.26188
/24312658 (Fraehr, 2024). We encourage readers to apply their
models using the different case studies provided in this paper and
compare them to the LSG model.

Declaration of competing interest

7. Conclusion

The authors declare that they have no known competing financial
interests or personal relationships that could have appeared to influence
the work reported in this paper.

In this study, we compared the LSG, 1dCNN, LSTM-SRR, GP-EOF,
and LSTM-EOF surrogate models for flood inundation modelling. These
surrogate models were all developed to be fast and accurate, and thus,
have the potential to be implemented in real-time forecasting and
ensemble modelling applications where computationally demanding
high-resolution hydrodynamic models are unfeasible. We applied the
surrogate models to the Chowilla floodplain and Burnett River in
Australia and Carlisle in the United Kingdom. We found that the LSG
model provided the most accurate simulations of the flood extent, peak
water depth, and the general dynamic evolution of the flood inundation.
All the surrogate models showed high computational efficiency
compared to the reference high-fidelity models with speed-up ratios
ranging from two to five orders of magnitude. The 1dCNN model is the
fastest of the surrogate models but cannot compete with the LSG model
in terms of accuracy.

Data availability

The data used for this manuscript is stored in an online reposiory. We
have shared the data by direct reference in the text of the manuscript.


#### Acknowledgments


Niels Fraehr acknowledges support from The University of Mel­
bourne via the Melbourne Research Scholarship, and Wenyan Wu ac­
knowledges support from the Australian Research Council via the
Discovery Early Career Researcher Award (DE210100117). We thank
SunWater and Murray-Darling Basin Authority for their permission to
use the case studies for the Burnett River and Chowilla floodplain,
respectively. We acknowledge BMT for providing a TUFLOW license to
conduct TUFLOW simulations for the Burnett River case study.

The LSG model is a physics-guided hybrid model that uses a low-
fidelity model to provide an initial estimate of the flood inundation
and subsequently upskills the low-fidelity estimate through the use of
EOF analysis and GP models. We found the low-fidelity model to be very
important to ensure high accuracy using the LSG model. The low-fidelity
model is physics-based and transforms the boundary inflows into
spatiotemporal flood inundation patterns while incorporating the hys­
teresis of the system. Surrogate models that accommodate hysteresis
through time-lagged input features (e.g. the GP-EOF and 1dCNN
models) struggle with the curse of dimensionality, resulting in reduced
accuracy, especially for river systems with numerous inflows as seen in
the Burnett River case study.


#### References


Abadi, M. I., Agarwal, A., Barham, P., Brevdo, E., Chen, Z., Citro, C., Greg Davis, A.,

Dean, J., Devin, M., Ghemawat, S., Goodfellow, I., Harp, A., Irving, G., Isard, M., Jia,
Y., Jozefowicz, R., Kaiser, L., Kudlur, M., … Zheng, X. (2016). TensorFlow: large-
scale machine learning on heterogeneous distributed systems. arXiv pre-print server.
10.48550/arXiv.1603.04467.
Bates, P.D., 2022. Flood inundation prediction. Annu. Rev. Fluid Mech. 54 (1), 287–315.

https://doi.org/10.1146/annurev-fluid-030121-113138.
Bates, P.D., De Roo, A.P.J., 2000. A simple raster-based model for flood inundation

For predicting flood events with inflows higher than those experi­
enced in training, all surrogate models struggle to produce accurate
predictions. The results are significantly improved when larger events
are included in the training data. For this reason, it is important to
incorporate a wide range of inundation behaviour in the training dataset

simulation. J. Hydrol. 236 (1-2), 54–77. https://doi.org/10.1016/s0022-1694(00)
00278-x.
Bauer, M., Wilk, M.v.d., Rasmussen, C.E., 2016. Understanding probabilistic sparse

Gaussian process approximations. In: Proceedings of the 30th International
Conference on Neural Information Processing Systems. Barcelona, Spain. https://
doi.org/10.48550/arxiv.1606.04820.

13

### Page 14

N. Fraehr et al.

Water Research 252 (2024) 121202

Bentivoglio, R., Isufi, E., Jonkman, S.N., Taormina, R., 2022. Deep learning methods for

equations. Ocean Eng. 248, 110775 https://doi.org/10.1016/j.
oceaneng.2022.110775.
Jamali, B., Bach, P.M., Cunningham, L., Deletic, A., 2019. A cellular automata fast flood

flood mapping: a review of existing applications and future research directions.
Hydrol. Earth Syst. Sci. 26 (16), 4345–4378. https://doi.org/10.5194/hess-26-4345-
2022.
Bentivoglio, R., Isufi, E., Jonkman, S.N., Taormina, R., 2023. Rapid spatio-temporal flood

evaluation (CA-ff´e) model. Water Resour. Res. 55 (6), 4936–4953. https://doi.org/

#### 10.1029/2018WR023679.

Jamali, B., Haghighat, E., Ignjatovic, A., Leit˜ao, J.P., Deletic, A., 2021. Machine learning

modelling via hydraulics-based graph neural networks. Hydrol. Earth Syst. Sci. 27
(23), 4227–4246. https://doi.org/10.5194/hess-27-4227-2023.
Bermúdez, M., Cea, L., Puertas, J., 2019. A rapid flood inundation model for hazard

for accelerating 2D flood models: potential and challenges. Hydrol. Process. 35 (4)
https://doi.org/10.1002/hyp.14064.
Kabir, S., Patidar, S., Xia, X.L., Liang, Q.H., Neal, J., Pender, G., 2020. A deep

mapping based on least squares support vector machine regression. J. Flood Risk
Manag. 12 (S1), e12522. https://doi.org/10.1111/jfr3.12522.
Bomers, A., Schielen, R.M.J., Hulscher, S., 2019. Application of a lower-fidelity surrogate

convolutional neural network model for rapid prediction of fluvial flood inundation.
J. Hydrol. 590, 16. https://doi.org/10.1016/j.jhydrol.2020.125481. Article 125481.
Karim, F., Armin, M.A., Ahmedt-Aristizabal, D., Tychsen-Smith, L., Petersson, L., 2023.

hydraulic model for historic flood reconstruction [Article] Environ. Model. Softw.
117, 223–236. https://doi.org/10.1016/j.envsoft.2019.03.019.
Brent Daniel, W., Roth, C., Li, X., Rakowski, C., McPherson, T., Judi, D., 2023. Extremely

A review of hydrodynamic and machine learning approaches for flood inundation
modeling. Water 15 (3). https://doi.org/10.3390/w15030566. Article 566.
Leijnse, T., van Ormondt, M., Nederhoff, K., van Dongeren, A., 2021. Modeling

rapid, Lagrangian modeling of 2D flooding: a rivulet-based approach. Environ.
Model. Softw. 161, 105630 https://doi.org/10.1016/j.envsoft.2023.105630.
Burt, D., Rasmussen, C.E., Wilk, M.V.D., 2019. Rates of convergence for sparse

compound flooding in coastal systems using a computationally efficient reduced-
physics solver: including fluvial, pluvial, tidal, wind- and wave-driven processes.
Coast. Eng. 163, 103796 https://doi.org/10.1016/j.coastaleng.2020.103796.
Lhomme, J., Sayers, P., Gouldby, B., Wills, M., Mulet-Marti, J., 2008. Recent

variational gaussian process regression. In: Proceedings of the 36th International
Conference on Machine Learning, Proceedings of Machine Learning Research.
https://doi.org/10.48550/arXiv.1903.03571.
Buttinger-Kreuzhuber, A., Konev, A., Horvath, Z., Cornel, D., Schwerdorf, I., Bloeschl, G.,

Development and Application of a Rapid Flood Spreading Method. CRC Press,
pp. 15–24. https://doi.org/10.1201/9780203883020.ch2.
Lin, Q., Leandro, J., Wu, W.R., Bhola, P., Disse, M., 2020. Prediction of maximum flood

Waser, J., 2022. An integrated GPU-accelerated modeling framework for high-
resolution simulations of rural and urban flash floods. Environ. Model. Softw. 156
https://doi.org/10.1016/j.envsoft.2022.105480. Article 105480.
Chang, L.C., Liou, J.Y., Chang, F.J., 2022. Spatial-temporal flood inundation nowcasts by

inundation extents with resilient backpropagation neural network: case study of
Kulmbach [Article] Front. Earth Sci. 8 (8). https://doi.org/10.3389/
feart.2020.00332. Article 332.
Liu, L., Liu, Y., Wang, X., Yu, D., Liu, K., Huang, H., Hu, G., 2015. Developing an effective

fusing machine learning methods and principal component analysis. J. Hydrol. 612,

#### 128086 https://doi.org/10.1016/j.jhydrol.2022.128086.

Chitwatkulsiri, D., Miyamoto, H., 2023. Real-time urban flood forecasting systems for

2-D urban flood inundation model for city emergency management based on cellular
automata. Nat. Hazards Earth Syst. Sci. 15 (3), 381–391. https://doi.org/10.5194/
nhess-15-381-2015.
L¨owe, R., B¨ohm, J., Jensen, D.G., Leandro, J., Rasmussen, S.H., 2021. U-

Southeast Asia-a review of present modelling and its future prospects. Water 15 (1).
https://doi.org/10.3390/w15010178. Article 178.
Coppede, A., Gaggero, S., Vernengo, G., Villa, D., 2019. Hydrodynamic shape

FLOOD–topographic deep learning for predicting urban pluvial flood water depth.
J. Hydrol. 603, 126898 https://doi.org/10.1016/j.jhydrol.2021.126898.
Luo, P., Luo, M., Li, F., Qi, X., Huo, A., Wang, Z., He, B., Takara, K., Nover, D., Wang, Y.,

optimization by high fidelity CFD solver and Gaussian process based response
surface method. Appl. Ocean Res. 90, 11. https://doi.org/10.1016/j.
apor.2019.05.026. Article 101841.
Devi, N.N., Sridharan, B., Kuiry, S.N., 2019. Impact of urban sprawl on future flooding in

2022. Urban flood numerical simulation: research, methods and future perspectives.
Environ. Model. Softw. 156, 105478 https://doi.org/10.1016/j.
envsoft.2022.105478.
Ma, P., Konomi, G. K. B. A., Asher, T. G., Toro, G. R., & Cox, A. T. (2019). Multifidelity

Chennai city, India. J. Hydrol. 574, 486–496. https://doi.org/10.1016/j.
jhydrol.2019.04.041.
Diederik, P.K., & Ba, J. (2017). Adam: a method for stochastic optimization. arXiv pre-

computer model emulation with high-dimensional output: an application to storm
surge. arXiv. 10.48550/ARXIV.1909.01836.
Maier, H.R., Galelli, S., Razavi, S., Castelletti, A., Rizzoli, A., Athanasiadis, I.N., S`anchez-

print server. 10.48550/arXiv.1412.6980.
do Lago, C.A.F., Giacomoni, M.H., Bentivoglio, R., Taormina, R., Gomes, M.N.,

Mendiondo, E.M., 2023. Generalizing rapid flood predictions to unseen urban
catchments with conditional generative adversarial networks. J. Hydrol. 618,

#### 129276 https://doi.org/10.1016/j.jhydrol.2023.129276.

Donnelly, J., Abolfathi, S., Pearson, J., Chatrabgoun, O., Daneshkhah, A., 2022. Gaussian

Marr`e, M., Acutis, M., Wu, W., Humphrey, G.B., 2023. Exploding the myths: an
introduction to artificial neural networks for prediction and forecasting. Environ.
Model. Softw. 167, 105776 https://doi.org/10.1016/j.envsoft.2023.105776.
Malde, S., Wyncoll, D., Oakley, J., Tozer, N., Gouldby, B., 2016. Applying emulators for

process emulation of spatio-temporal outputs of a 2D inland flood model. Water Res.
225, 119100 https://doi.org/10.1016/j.watres.2022.119100.
Fraehr, N., 2024. Surrogate flood model comparison - Datasets and python code (Version 1).

improved flood risk analysis. E3S Web Conf. 7, 04002. https://doi.org/10.1051/
e3sconf/20160704002.
Matthews, A.G.D.G., Wilk, M.V.d., Nickson, T., Fujii, K., Boukouvalas, A., Le´on-

The University of Melbourne. https://doi.org/10.26188/24312658.
Fraehr, N., Wang, Q.J., Wu, W., Nathan, R., 2022. Upskilling low-fidelity hydrodynamic

Villagr´a, P., Ghahramani, Z., Hensman, J., 2017. GPflow: a Gaussian process library
using TensorFlow. J. Mach. Learn. Res. 18 (40), 1–6. http://jmlr.org/papers/v18/16
-537.html.
Menberg, K., Bidarmaghz, A., Gregory, A., Choudhary, R., Girolami, M., 2020. Multi-

models of flood inundation through spatial analysis and Gaussian Process learning.
Water Resour. Res. 58 (8), e2022WR032248 https://doi.org/10.1029/

#### 2022WR032248.

Fraehr, N., Wang, Q.J., Wu, W., Nathan, R., 2023a. Development of a fast and accurate

fidelity approach to Bayesian parameter estimation in subsurface heat and fluid
transport models. Sci. Total Environ. 745, 140846 https://doi.org/10.1016/j.
scitotenv.2020.140846.
Ming, X., Liang, Q., Xia, X., Li, D., Fowler, H.J., 2020. Real-time flood forecasting based

hybrid model for floodplain inundation simulations. Water Resour. Res. 59 (6),
e2022WR033836 https://doi.org/10.1029/2022WR033836.
Fraehr, N., Wang, Q.J., Wu, W., Nathan, R., 2023b. Supercharging hydrodynamic

on a high-performance 2-D hydrodynamic model and numerical weather predictions.
Water Resour. Res. 56 (7) https://doi.org/10.1029/2019wr025583.
Morales-Hern´andez, M., Sharif, M.B., Kalyanapu, A., Ghafoor, S.K., Dullo, T.T.,

inundation models for instant flood insight. Nat. Water. https://doi.org/10.1038/
s44221-023-00132-2.
Gu, M., Berger, J.O., 2016. Parallel partial Gaussian process emulation for computer

Gangrade, S., Kao, S.C., Norman, M.R., Evans, K.J., 2021. TRITON: a multi-GPU
open source 2D hydrodynamic flood model. Environ. Model. Softw. 141, 105034
https://doi.org/10.1016/j.envsoft.2021.105034.
Mosavi, A., Ozturk, P., Chau, K.W., 2018. Flood prediction using machine learning

models with massive output. Ann. Appl. Stat. 10 (3), 1317–1347. http://www.jstor.
org/stable/43956883.
Guha-Sapir, D., Below, R., Hoyois, P., 2023. EM-DAT: The CRED/OFDA International

Disaster Database. Universit´e Catholique de Louvain, Brussels, Belgium [Database].
www.emdat.be.
Guo, K., Guan, M., Yu, D., 2021. Urban surface water flood modelling – a comprehensive

models: literature review [Review] Water 10 (11), 40. https://doi.org/10.3390/
w10111536. Article 1536.
Mu˜noz, D.F., Mu˜noz, P., Moftakhari, H., Moradkhani, H., 2021. From local to regional

review of current models and future challenges. Hydrol. Earth Syst. Sci. 25 (5),
2843–2860. https://doi.org/10.5194/hess-25-2843-2021.
He, J., Zhang, L., Xiao, T., Wang, H., Luo, H., 2023. Deep learning enables super-

compound flood mapping with deep learning and data fusion techniques. Sci. Total
Environ. 782, 146927 https://doi.org/10.1016/j.scitotenv.2021.146927.
Neal, J., Fewtrell, T., Trigg, M., 2009. Parallelisation of storage cell flood models using

resolution hydrodynamic flooding process modeling under spatiotemporally varying
rainstorms. Water Res. 239, 120057 https://doi.org/10.1016/j.watres.2023.120057.
Hou, J., Li, X., Bai, G., Wang, X., Zhang, Z., Yang, L., Du, Y.e., Ma, Y., Fu, D., Zhang, X.,

OpenMP. Environ. Model. Softw. 24 (7), 872–877. https://doi.org/10.1016/j.
envsoft.2008.12.004.
Neal, J., Keef, C., Bates, P., Beven, K., Leedal, D., 2013. Probabilistic flood risk mapping

2021. A deep learning technique based flood propagation experiment. J. Flood Risk
Manag. 14 (3), e12718. https://doi.org/10.1111/jfr3.12718.
Hu, R., Fang, F., Pain, C.C., Navon, I.M., 2019. Rapid spatio-temporal flood prediction

including spatial dependence. Hydrol. Process. 27 (9), 1349–1363. https://doi.org/
10.1002/hyp.9572.
Nobre, A.D., Cuartas, L.A., Momo, M.R., Severo, D.L., Pinheiro, A., Nobre, C.A., 2016.

and uncertainty quantification using a deep learning method. J. Hydrol. 575,
911–920. https://doi.org/10.1016/j.jhydrol.2019.05.087.
Huxley, C., Syme, B., 2016. TUFLOW GPU – best practice advice for hydrologic and

HAND contour: a new proxy predictor of inundation extent. Hydrol. Process. 30 (2),
320–333. https://doi.org/10.1002/hyp.10581.
OpenStreetMap. (2023). OpenTopoMap. https://www.openstreetmap.org/copyright.
Parkes, B.L., Cloke, H.L., Pappenberger, F., Neal, J., Demeritt, D., 2013. Reducing

hydraulic model simulations. In: Proceedings of the Hydrology and Water Resources
Symposium. Queenstown (Huxley).
IPCC, 2021. Climate Change 2021: the physical science basis. Contribution of Working

inconsistencies in point observations of maximum flood inundation level. Earth
Interact. 17 (6), 1–27. https://doi.org/10.1175/2012EI000475.1.
Razavi, S., Tolson, B.A., Burn, D.H., 2012. Review of surrogate modeling in water

Group I to the Sixth Assessment Report of the Intergovernmental Panel on Climate
Change. Cambridge University Press. https://doi.org/10.1017/9781009157896. In
Press.
Jagtap, A.D., Mitsotakis, D., Karniadakis, G.E., 2022. Deep learning of inverse water

resources. Water Resour. Res. 48 (7) https://doi.org/10.1029/2011WR011527.
Read, J.S., Jia, X., Willard, J., Appling, A.P., Zwart, J.A., Oliver, S.K., Karpatne, A.,

Hansen, G.J.A., Hanson, P.C., Watkins, W., Steinbach, M., Kumar, V., 2019. Process-
guided deep learning predictions of lake water temperature. Water Resour. Res. 55
(11), 9173–9190. https://doi.org/10.1029/2019wr024922.

waves problems using multi-fidelity data: application to Serre–Green–Naghdi

14

### Page 15

N. Fraehr et al.

Water Research 252 (2024) 121202

Sanders, B.F., Schubert, J.E., 2019. PRIMo: parallel raster inundation model. Adv. Water

Thenon, A., Gervais, V., Ravalec, M.L., 2016. Multi-fidelity meta-modeling for reservoir

Resour. 126, 79–95. https://doi.org/10.1016/j.advwatres.2019.02.007.
Schaefer, J.T., 1990. The critical success index as an indicator of warning skill. Weather

engineering - application to history matching. Comput. Geosci. 20 (6), 1231–1250.
https://doi.org/10.1007/s10596-016-9587-y.
US Army Corps of Engineers. (2021). Hydraulic Reference Manual [Computer Program

Forecast. 5 (4), 570–575.doi:10.1175/1520-0434(1990)005<0570:Tcsiaa>2.0.Co;2
Sit, M., Demiray, B.Z., Xiang, Z., Ewing, G.J., Sermet, Y., Demir, I., 2020.

Documentation](HEC-RAS - River Analysis System, Issue Version 6.0).
Wright, S., 1921. Correlation and causation. J. Agric. Res. 20 (7), 557–580.
Zheng, Q., Zhang, J., Xu, W., Wu, L., Zeng, L., 2019. Adaptive multifidelity data

A comprehensive review of deep learning applications in hydrology and water
resources. Water Sci. Technol. 82 (12), 2635–2670. https://doi.org/10.2166/
wst.2020.369.
Sridharan, B., Bates, P.D., Sen, D., Kuiry, S.N., 2021. Local-inertial shallow water model

assimilation for nonlinear subsurface flow problems. Water Resour. Res. 55 (1),
203–217. https://doi.org/10.1029/2018WR023615.
Zhou, Y., Wu, W., Nathan, R., Wang, Q.J., 2021. A rapid flood inundation modelling

on unstructured triangular grids. Adv. Water Resour. 152 https://doi.org/10.1016/j.
advwatres.2021.103930. Article 103930.
Teng, J., Jakeman, A.J., Vaze, J., Croke, B.F.W., Dutta, D., Kim, S., 2017. Flood

framework using deep learning with spatial reduction and reconstruction. Environ.
Model. Softw. 143, 105112 https://doi.org/10.1016/j.envsoft.2021.105112.
Zhou, Y., Wu, W., Nathan, R., Wang, Q.J., 2022. Deep learning-based rapid flood

inundation modelling: a review of methods, recent advances and uncertainty
analysis. Environ. Model. Softw. 90, 201–216. https://doi.org/10.1016/j.
envsoft.2017.01.006.
Teng, J., Vaze, J., Dutta, D., Marvanek, S., 2015. Rapid inundation modelling in large

inundation modeling for flat floodplains with complex flow paths. Water Resour.
Res. 58 (12) https://doi.org/10.1029/2022WR033214 e2022WR033214.
Zhu, C., Byrd, R.H., Lu, P., Nocedal, J., 1997. Algorithm 778: L-BFGS-B: fortran

floodplains using LiDAR DEM. Water Resour. Manag. 29 (8), 2619–2636. https://
doi.org/10.1007/s11269-015-0960-8.
Teng, J., Vaze, J., Kim, S., Dutta, D., Jakeman, A.J., Croke, B.F.W., 2019. Enhancing the

subroutines for large-scale bound-constrained optimization. ACM Trans. Math.
Softw. 23 (4), 550–560. https://doi.org/10.1145/279232.279236.
Zischg, A.P., Felder, G., Mosimann, M., Rothlisberger, V., Weingartner, R., 2018.

capability of a simple, computationally efficient, conceptual flood inundation model
in hydrologically complex terrain. Water Resour. Manag. 33 (2), 831–845. https://
doi.org/10.1007/s11269-018-2146-7.

Extending coupled hydrological-hydraulic model chains with a surrogate model for
the estimation of flood losses [Article] Environ. Model. Softw. 108, 174–185.
https://doi.org/10.1016/j.envsoft.2018.08.009.

15
