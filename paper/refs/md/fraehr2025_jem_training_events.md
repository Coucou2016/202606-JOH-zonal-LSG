# Fraehr et al. Generation and selection of training events for surrogate flood inundation models, Journal of Environmental Management

- **DOI:** https://doi.org/10.1016/j.jenvman.2024.123570
- **Local PDF:** `paper/refs/pdf/1-s2.0-S0301479724035564-main.pdf`
- **Access:** full text obtained (user-supplied publisher PDF)
- **Conversion tool:** PyMuPDF (`fitz`) via `paper/refs/_pdf_to_md.py`
- **Pages:** 15

---

## Extracted full text (OCR-free PDF text layer)

### Page 1

Journal of Environmental Management 373 (2025) 123570

Contents lists available at ScienceDirect

Journal of Environmental Management

journal homepage: www.elsevier.com/locate/jenvman

Research article

Generation and selection of training events for surrogate flood
inundation models

Niels Fraehr *, Quan J. Wang , Wenyan Wu , Rory Nathan

Department of Infrastructure Engineering, Faculty of Engineering and Information Technology, The University of Melbourne, Victoria, 3010, Australia


#### A R T I C L E I N F O



#### A B S T R A C T


The destructive and life-threatening nature of flood events calls for fast and accurate methods to predict dynamic
flood behaviour. Data-driven surrogate models have been developed to quickly predict flood inundation, though
their accuracy relies on the available flood information for model training and validation. Flood observations are
rarely available at high spatial and temporal scales, and thus computationally expensive high-resolution hy­
drodynamic (high-fidelity) models are often used to generate training data through simulation of selected flood
events. Given finite resources, only a limited number of events can be simulated using a high-fidelity model.
However, there is no established approach for selecting representative and informative flood events to ensure
that the surrogate model is robustly trained. In this study, a novel systematic approach for selecting flood events
for the training of surrogate flood inundation models is introduced. The approach generates a large set of
candidate events using a computationally efficient low-resolution hydrodynamic (low-fidelity) model and then
selects training events based on the simulated spatial-temporal inundation depths of the candidate events. The
approach is used to train surrogate models to predict flood inundation in three distinct case studies with different
boundary conditions and topographies. The results show robust performance of the surrogate models developed
with RMSE<0.23 m when applied to new unseen events, which is similar to the accuracy achieved when using all
available candidate events for training. This means the proposed training event selection approach reduces the
computational costs of generating training data by up to 97% as fewer high-fidelity model simulations are
needed, highlighting the computational advantage of the approach. Although this study focuses on surrogate
models for the prediction of flood inundation dynamics, the new approach could easily be used for the devel­
opment of surrogate models in other fields.

Handling editor: Lixiao Zhang

1. Introduction

flooding (DHI, 2019; TUFLOW, 2020; US Army Corps of Engineers,
2024). High-fidelity models are physics-based and solve governing
equations describing the conversation of momentum and mass balance
on a high-resolution numerical grid. This makes high-fidelity models
able to capture flood inundation dynamics with a high degree of realism,
but despite their accuracy, high-fidelity models are computationally
expensive (Teng et al., 2017). Surrogate models have been developed to
address this issue, as they can quickly provide inundation estimates of
imminent flood events (Bentivoglio et al., 2022; Karim et al., 2023;
Mosavi et al., 2018). Recently, development and use of data-driven (i.e.
machine learning and deep learning-based) surrogate models for flood
inundation modelling have risen in popularity (e.g. Bentivoglio et al.
(2023); Bermudez et al. (2018); Chu et al. (2020); Donnelly et al. (2024);
Liao et al. (2023); Xie et al. (2021); Zhou et al. (2022)), due to their high
computational efficiency and ability to predict non-linear relationships

Floods increasingly affect populated areas (Tellman et al., 2021),
resulting in loss of lives and damage to infrastructure (Guha-Sapir et al.,
2024). Climate change projections suggest that this trend is going to
continue in future decades (IPCC, 2021). Flooding is the dynamic pro­
cess of inundation of otherwise dry land and is usually driven by over­
flow from rivers (fluvial), rainfall (pluvial), storm surge, or a
combination of two or more flood drivers (compound) (Santiago-Collazo
et al., 2019; Xu et al., 2023). Computationally efficient methods that can
accurately simulate dynamic flooding behaviour are needed to enable
fast decision-making and response in times of flood emergencies. In such
situations, it is often not feasible to use complex high-resolution hy­
drodynamic (high-fidelity) models. High-fidelity models have been
continuously developed over the last decades to accurately simulate

* Corresponding author.
E-mail address: n.fraehr@unimelb.edu.au (N. Fraehr).

https://doi.org/10.1016/j.jenvman.2024.123570
Received 4 July 2024; Received in revised form 27 October 2024; Accepted 30 November 2024

Available online 6 December 2024
0301-4797/© 2024 The Authors. Published by Elsevier Ltd. This is an open access article under the CC BY license ( http://creativecommons.org/licenses/by/4.0/ ).

### Page 2

N. Fraehr et al.
Journal of Environmental Management 373 (2025) 123570

(Bentivoglio et al., 2022; Razavi et al., 2012).

based on the maximum inundation extent and depth, as well as Empir­
ical Orthogonal Functions (EOF) analysis of the spatio-temporal inun­
dation patterns. The approach ensures only the most important flood
events are selected for training, thus reducing the number of events
needed to be run using a computationally demanding high-fidelity
model. Furthermore, this approach also ensures robust training of the
surrogate model, enabling accurate predictions for new flood events not
included in training. For the sake of brevity, the approach is referred to
as LESS (Low-fidelity and EOF analysis Sampling Strategy). The per­
formance of LESS is assessed using three case studies in the United
Kingdom and Australia. In this assessment the accuracy is compared for
surrogate models trained using (I) available historic events, (II) historic
events and the maximum inundation candidate events, (III) historic
events and the full set of candidate events, and (IV) events selected using

#### LESS.


Data-driven surrogate models need to be trained before being
applied to make predictions, and thus the accuracy of the predictions
using these models depends on the training data used (Maier et al., 2023;
Maier et al., 2023). Ideally, the training data should be of sufficient
spatial and temporal resolution, accuracy, and cover a wide range of
possible flooding behaviours, for the surrogate model to be able to
provide useful predictions. The term “flooding behaviour” is used here
to refer to the spatio-temporal variations in the extent and depth of
water in over-bank areas associated with the rising and falling periods (i.
e. flooding and drying) of a flood event. Capturing wide-ranging
flooding behaviours for the training data can rarely be achieved by
simply using observations (Bentivoglio et al., 2022). Consequently, re­
searchers and model developers often generate training data using a
high-fidelity model (e.g. Chang et al. (2022); Fauzi and Mizutani (2020);
Liao et al. (2023); Lin et al. (2020); Zhou et al. (2022)). When using a
high-fidelity model to generate data for the training of surrogate models,
the high-fidelity model should be well-calibrated to describe flooding
behaviours that are as close to reality as possible because any errors in
the high-fidelity model will be inherited by the surrogate model through
the training process.

The rest of the paper is organised as follows. In Section 2, the
methodology and application of LESS is described. In Section 3 the re­
sults are presented, followed by discussion and conclusion in Sections 4
and 5, respectively.

2. Methods and materials

The process of generating training data requires running the high-
fidelity model for a selected set of flood events, which can be compu­
tationally expensive. This means for projects with a limited computa­
tional budget, there is only sufficient time to run a small number of
carefully selected flood events. The selected flood events should cover a
wide range of flooding behaviours to include sufficient information to
ensure reliable predictions using the trained surrogate model. It is
important to select the most suitable events given the limited compu­
tational budget. In previous studies, various approaches have been used
to train surrogate models for flood inundation. For example, Kabir et al.
(2020), Fraehr et al. (2023a) and Donnelly et al. (2022) used scaled
historic events, He et al. (2023) used design rainfall events with constant
rainfall rates and uniform spatial distribution, Contreras et al. (2020)
used historic events exceeding a given inflow threshold, and Lin et al.
(2020) used synthetic events of various sizes. However, in these studies,
the selection of specific events for surrogate model training is often not
justified or based on an ad hoc approach, for example using
trial-and-error, based on data availability, or the model developer’s
knowledge of the specific model and case study. Therefore, there is a
need to establish a systematic approach to select flood events for
training surrogate flood inundation models.

Accurate prediction of flooding using surrogate models requires a
wide range of flooding behaviour to be included in the training data. For
this purpose, this study introduces LESS to select flood events to train
surrogate flood inundation models. Details of LESS are provided below,
and this is followed by a description of its application to various case
studies in Section 2.2.

2.1. Methodology of LESS for selecting training events

LESS is a method to select flood inundation events that will be
simulated using a computationally demanding high-fidelity model to
produce data for training surrogate models. The aim of LESS is to select a
minimum number of training events that cover a wide range of flooding
behaviours to ensure robust training of a surrogate flood inundation
model. The process of LESS is illustrated in Fig. 1. To exemplify the
concepts involved, the statistical characteristics of the flood events (i.e.
the spatio-temporal evolution of the extent and depth of inundation) are
illustrated as two-dimensional figures, where each figure corresponds to
a single flood event.

The surrogate model needs to be trained using flood events simulated
using a high-fidelity model. High-fidelity models need to be calibrated
using historic events to provide accurate simulations of flooding for a
given case study. Given the effort involved in obtaining the necessary
training data and undertaking model calibration, it may be assumed that
there is only a small number of historic events available for the cali­
bration. As a first step, LESS includes the available historic events as
training events (Step 1).

In the wider environmental modelling field, event selection strate­
gies have been developed based on various information, including
model inputs. For example, Sun and Bertrand-Krajewski (2012) used a
ranking approach to select inputs for stormwater quality modelling, and
Jam-Jalloh et al. (2023) used a wavelet analysis approach to select
events for hydrological modelling. However, these approaches cannot
easily be transferred to assist the selection of flood events for training
surrogate flood inundation models. The flooding behaviour encountered
during flood events depends on the hysteresis of the system, the shape,
timing, and magnitude of the boundary conditions (i.e. time series of
flood drivers such as river flow, water levels, rainfall etc.), catchment
topography, and roughness (Bates, 2022; Teng et al., 2017). An
approach used for selecting training events for surrogate models for
flood inundation should therefore incorporate information from
two-dimensional flood maps covering a wide range of flooding
behaviours.

The available historical events are often not sufficient to represent
the full range of expected flooding behaviours, thus additional flood
events suitable for training are obtained by scaling the boundary con­
ditions of the available historical events to generate a set of candidate
events (Step 2). The subsequent choices of candidate events to include in
the training data set are selected to ensure maximum diversity in the
range of flooding behaviours.

The selection of candidate events should be based on the flooding
characteristics of each candidate event (i.e. the hysteresis of the system,
boundary conditions, catchment topography, and roughness). For that
reason, the full set of candidate events is simulated using a computa­
tionally efficient low-fidelity model to provide approximate estimates of
their associated inundation extents and depths. The purpose is to
generate a data set that is representative of a wide range of flood be­
haviours, which will then be statistically characterised to provide
objective measures of the observed differences involved. Even though
the low-fidelity model is only able to provide approximate estimates, it

Here we introduce a novel approach to select flood events for
training surrogate flood inundation models. The approach relies on the
use of a simplified and super-fast low-resolution hydrodynamic (Low-
fidelity) model to simulate flood inundation for a large set of candidate
events. Then, the results from the simulated candidate events are used to
select the subset of candidate events that provide the best coverage of
possible flooding behaviours. This subset of candidate events is selected
to include events that result in a wide range of flooding behaviours

2

### Page 3

N. Fraehr et al.
Journal of Environmental Management 373 (2025) 123570

Fig. 1. Figurative example of LESS using two-dimensional figures with different shapes, colours, and sizes to represent historic (H) and candidate (C) flood events
with diverse flooding behaviour.

is a suitable means for characterising relative differences in flood
behaviour in a consistent manner. The figures in Fig. 1 represent the
statistical characteristics of the flood events based on the low-fidelity
model results.

flooding behaviour are iteratively selected (Step 4). In the first iteration,
the training events selected are the available historic events and the
subset of maximum inundation candidate events. Subsequent iterations
involve selecting candidate events that are most different to the events
retained in the training set and including these candidate events for
training. This iterative process is continued until a pre-determined
number of training events have been selected. Finally, the selected
training events are simulated using the high-fidelity model, and the
results can be used to train the surrogate model. The details of each step
of LESS are described in the following Sections 2.1.1 to 2.1.4.

From the low-fidelity model results, the largest candidate events
resulting in maximum inundation extents and depths are selected for
training (Step 3). These maximum inundation events cover the widest
range of possible flooding behaviours and ensure the training data in­
cludes information in all areas likely to get flooded.

The maximum inundation events define the envelope of the spatial
extent of the candidate events. However, the training data also needs to
span differences in spatio-temporal inundation dynamics, and thus
additional candidate events need to be selected to ensure robust training
of the surrogate model. To increase the number of candidate events
considered, the candidate events that exhibit the most diverse range of

2.1.1. Step 1: Initial selection of available historical events
When selecting training events for training a surrogate flood inun­
dation model, LESS starts by including available historic events that
have already been simulated using a high-fidelity model. If the high-

3

### Page 4

N. Fraehr et al.
Journal of Environmental Management 373 (2025) 123570

fidelity model has been used to simulate a wide range of events, these
events may be sufficient to train the surrogate model and no additional
high-fidelity simulations are needed. However, often only a few high-
fidelity simulations are available and new training events have to be
simulated to ensure a wide range of flooding behaviours are included in
the training data.

inundation behaviour of a flood event as shown by Fraehr et al. (2023b).
Leveraging this ability, the low-fidelity model results are used to
distinguish the flooding behaviour of each candidate event and select
appropriate training events. The selection of training events from the
low-fidelity model results is explained in the following sections.

2.1.3. Step 3: Selection of maximum inundation candidate events
The surrogate model should be able to predict flooding in all areas (i.
e. computational grid cells) that are likely to get flooded. This is ensured
by finding the combined maximum inundation extent across the full set
of candidate events. The combined maximum inundation extent will
often comprise only a few large candidate events, as the inundation
extents of larger events will overlap with the extents of smaller events.

2.1.2. Step 2: Generation of candidate events
In cases where there is a limited range of high-fidelity simulations
available, it is necessary to simulate new events using the high-fidelity
model to provide additional training data for the surrogate model.
These additional training events are selected from a set of candidate
events.

The candidate events are generated by scaling up and/or down the
magnitude of boundary conditions (e.g. the time series of flood drivers
such as river flow, water levels, and rainfall) of historic events. Only the
magnitude of the boundary conditions is scaled to ensure the timing
between the flood drivers is physically possible for the case study for
which the surrogate model is applied. In this study, we created scaled
versions of available historic events that have already been simulated
using a high-fidelity model (See Section 2.2). If no or only a few of these
historical events are available, new events should be identified from the
historical records of the boundary conditions.

The subset of candidate events that contribute to the combined
maximum inundation extent (referred to here as “maximum inundation
candidate events”) is found by considering the events that result in the
maximum water depth in each grid cell across the whole model domain,
as demonstrated in Fig. 2. As can be seen in the figure, candidate Event 3
results in the highest water depth for 69% of the combined maximum
inundation extent, candidate Event 1 results in the highest water depth
for 18% of the combined maximum inundation extent and so forth. The
subset of the first few candidate events that contribute to at least 90% of
the combined maximum inundation extent is included as training
events. In Fig. 2, this means Events 3, 1, and 5 are included as training
events. This 90% threshold was found in the initial testing to reduce the
number of maximum inundation candidate events selected for training
while allowing for robust training of the surrogate model. The extent of
the events selected using the 90% threshold should extend to the full
limits of the combined maximum inundation extent across the full set of
candidate events. This means, as shown in Fig. 2, if the green areas
where Event 2 resulted in the maximum water depth are also inundated
during Events 3, 1, or 5, but just at lower water depths, then Events 3, 1
and 5 are confirmed as maximum inundation candidate events. If this is
not the case, then Event 2 is considered a maximum inundation candi­
date event and included for training. This check is performed for all
candidate events that are excluded by the 90% threshold.

In practice, the method used to scale the magnitude of the boundary
conditions should consider the physical properties of the type of
boundary condition. For example, flow and rainfall boundary conditions
can be scaled by multiplying by a factor, whereas water levels are usu­
ally raised or lowered by adding a constant value to make sure unreal­
istically high water levels are not created unintentionally. Section 2.2.2
provides practical examples of how to scale boundary conditions for
three case studies.

Flood events are often the result of compound factors, thus the high-
fidelity model can have several boundary conditions. The magnitude of
each boundary condition is scaled within the range of values it may take
(e.g., between a 2 and 500-year return period, or a specific range of peak
flow rates to which the surrogate model is going to be applied). The set
of ncand candidate events with boundary conditions of varying magni­
tudes are created following equation (1).

2.1.4. Step 4: Iterative selection of training events with the most diverse
flooding behaviours

∏
nbc

The training events should represent a wide variety of flooding be­
haviours to ensure robust training of the surrogate model that results in
accurate predictions for new unseen events. Although the concept of
including events that “represent a wide range of flooding behaviours”
may be straightforward (i.e. large and small events, events of different
timing, events resulting from different combinations of flood drivers),

ncand = nhist •

nscales(i)
(1)

i=1

where ncand is the number of candidate events, nhist is the number of
historic events to be scaled, nbc is the number of boundary conditions,
and nscales is the number of scaled versions of boundary condition i.

After scaling the boundary conditions for the set of candidate events,
estimates of the flood inundation depths and extents are obtained for
each candidate event using a low-fidelity model. The low-fidelity model
is a simplified version of the high-fidelity model that is computationally
efficient and can provide estimates of flood inundation in a small frac­
tion of the time required by the original high-fidelity model (Razavi
et al., 2012). The low-fidelity model is normally developed by coars­
ening the computational grid, extending the computational timesteps
and simplifying the physical representation of the flood inundation by
assumptions of the governing equations (Asher et al., 2015; Fraehr et al.,
2023b; Razavi et al., 2012). The accuracy of flood inundation simula­
tions depends on how well a model describes the hysteresis of the sys­
tem, boundary conditions, catchment topography and roughness (Bates,
2022; Teng et al., 2017). A low-fidelity model has reduced accuracy
compared to its high-fidelity counterpart, as the low-fidelity model
employs simplifications of the geometry and physical representation.
However, the low-fidelity model, just as the case for the high-fidelity
model, is governed by equations describing the conversation of mo­
mentum and mass (Bates, 2022; Teng et al., 2017), thus ensuring a
physical foundation for the simulations. This means that even an
extremely simplified low-fidelity model can capture the main flood

Fig. 2. Selection of maximum inundation candidate events. The coloured areas
indicate the proportion of the combined maximum inundation extent resulting
from each candidate event.

4

### Page 5

N. Fraehr et al.
Journal of Environmental Management 373 (2025) 123570

the actual process of selecting such events directly from the full set of
candidate events is a challenging task. The low-fidelity simulation re­
sults provide a time series of flood maps (i.e. water depth hydrographs
for all computational grid cells) for each candidate event. Consequently,
the selection of training events is a multi-dimensional problem that goes
beyond the magnitude of flood drivers, such as inflow. Therefore, EOF
analysis is used as part of LESS to characterise the flooding behaviour
and capture the most important information in the low-fidelity simula­
tions. The details of the EOF analysis are provided below.

where XAll is the dataset of all the flood events stacked into a T × N
matrix, T is the number of total timesteps in all the flood events, N is the
number of grid cells inundated in all the flood events, UAll is a T × N
matrix in which each row corresponds to a spatial component derived
for the flood events, CAll is a T × T matrix in which each column cor­
responds to an EC derived for the flood events.

Each row of the ECs matrix CAll corresponds to one timestep of the
flood inundation results, that is one flood map in the original high-
dimensional space. The ECs can therefore be used to represent the
high-dimensional dataset of all low-fidelity results as K time series in a
latent space. The K ECs time series allow us to statistically characterise
the flooding behaviours of the flood events. By identifying the degree of
similarity between timesteps in the time series, the timesteps exhibiting
significantly diverse flooding behaviour can be identified and the cor­
responding flood events can be selected for training (See Section
2.1.4.2).
The number of K modes to derive via the EOF analysis is important to
describe the degree of similarity between timesteps. The first two modes
(i.e., K = 2) usually describe a large proportion of the variance, and by
considering only the first two ECs time series, the high-dimensional
flood inundation data can easily be visualised as a two-dimensional
scatter plot by plotting ECs time series 1 (i.e. first column in CAll)
against ECs time series 2 (i.e. second column in CAll) as shown in Fig. 3.
Two points located close to one another in this two-dimensional latent
space represent similar flooding behaviours, and conversely, two points
that are distant from each other indicate dissimilar flooding behaviours.
Although using two modes is useful for the visualisation of the data in
the latent space, more modes are usually required to describe the
complexity of the flood inundation data. The number of K significant
modes is found through the use of North’s test (North et al., 1982) and
Kaiser’s Rule (Kaiser, 1960) following the study by Fraehr et al.,

2.1.4.1. Statistically summarising flooding behaviour using EOF analysis.
EOF analysis (also referred to as Principal Component Analysis or Proper
Orthogonal Decomposition) is a methodology to reduce the dimen­
sionality of correlated data sets that vary in space and time and has been
used in various studies for the dimensional reduction of flood inundation
surfaces (e.g. Aires et al. (2014); Aires et al. (2020); Chang et al. (2023);
Fraehr et al. (2022)). EOF analysis deconstructs the spatio-temporal
low-fidelity inundation results into pairs of spatial and temporal com­
ponents through singular value decomposition (See Equation (2))
(Jolliffe and Cadima, 2016). The temporal components are referred to as
Expansion Coefficients (ECs) and the pairs of spatial components and
ECs are usually referred to as modes. Each mode is independent of other
modes and describes a decreasing proportion of the variance in data.
Therefore, the dimensional reduction of the EOF analysis is achieved by
using a small number (K) of the most significant modes to represent the
majority of the variance in the dataset. The EOF analysis is applied to the
historic and full set of candidate events stacked as one long time series of
flood maps, following the same procedure as outlined in Fraehr et al.
(2023a).

∑
K

XAll = UAll • CAll ≈

UAll(k, :) • CAll(:, k)
(2)

k=1

Fig. 3. The iterative process of selecting additional candidate events to include as training events based on the Euclidean distance in the ECs latent space.

5

### Page 6

N. Fraehr et al.
Journal of Environmental Management 373 (2025) 123570

(2023a). Further details of the EOF analysis are included in studies by
Aires et al. (2014); Fraehr et al. (2023a); Hannachi et al. (2007); Jolliffe
and Cadima (2016).

throughout the full set of candidate events. In other words, nevents should
be high enough so that the selected training events (blue crosses) cover
the same latent space as the full set of candidate events (grey circles) in
Fig. 2.3.

After selecting nevents training events, the high-fidelity model is run
for the selected training events and the results can be used to train a
surrogate model to provide computationally efficient predictions of
flood inundation for new events.

2.1.4.2. Identifying the candidate event with the most diverse flooding
behaviour. The candidate events that have the most diverse flooding
behaviours compared to the training events already selected should be
included for training to ensure wide-ranging flooding behaviours in the
training data. To compare the similarity between already selected
training events and candidate events, CAll is separated into subsets CTrain
and CCand, that contains the rows (i.e. flood maps) of CAll for the already
selected training events and remaining candidate events, respectively.
Thus, the candidate events with the most diverse flooding behaviours
are found by considering the maximum Euclidean distance between any
candidate event ECs timestep in CCand and any training event ECs
timestep in CTrain (See Equation (3)). The candidate event, that contains
the ECs timestep (i.e. flood map) resulting in the maximum distance, is
considered to have the most diverse flooding behaviour. This candidate
event is included as an additional training event to diversify the training
events as much as possible.

2.2. Application of LESS

The process of developing the surrogate model is shown in Fig. 4.
First, the training events are selected using LESS, then the training
events are simulated using a high-fidelity model, and finally, the sur­
rogate model is trained and used for the prediction of new unseen
events. The application of LESS is demonstrated using the LSG surrogate
model and three case studies, which are described below.

2.2.1. Choice of surrogate model
The Low-fidelity, Spatial Analysis, and Gaussian Process (LSG) model
is chosen as the surrogate model used in this study. The LSG model uses a
low-fidelity model (i.e. a low-resolution and simplified hydrodynamic
model that is highly computationally efficient) to provide an initial es­
timate of the flood inundation in a study area. This estimate is then
transformed to high resolution and accuracy using EOF analysis and
Sparse Gaussian Process models. The LSG model has been continuously
developed (Fraehr et al., 2022, 2023a, 2023b), and has been shown to
provide more accurate predictions of spatio-temporal flood inundation
than other data-driven surrogate models (Fraehr et al., 2024). The use of
the LSG model allows the same low-fidelity model to be used both in
LESS for selecting training events and in the LSG surrogate model for
predicting flood inundation. For the details of the LSG model, readers
are referred to Fraehr et al. (2023a, 2023b).

(

b∈CTrain̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅
(a −b)2
√
)

Cmax

Cand = arg

max
a∈CCand min

(3)

where Cmax

cand is the timestep in a candidate event resulting in the
maximum distance from any of the timesteps in the training events.

The procedure of selecting the candidate events using EOF analysis
to represent the flooding behaviours is an iterative process, as shown in
Fig. 3. Each candidate event consists of a time series of flood maps,
meaning each point in the figure corresponds to a unique timestep (i.e.
flood map) in the ECs latent space. The figure only shows the first two
dimensions of the latent space, but in reality, there are K dimensions. In
the first iteration, the selected training events consist of the historic
events selected in Section 2.1.1 and the subset of maximum inundation
candidate events selected in Section 2.1.3. Thereafter a new candidate
event is selected for training at each iteration based on the Euclidean
distance between candidate and training events in the ECs latent space
as described above. At each iteration, the newly selected training event
is added to CTrain. When more events are selected for training, the
selected training events become increasingly representative of the full
set of candidate events. The iterative process is repeated until a pre­
determined number of events nevents has been selected for training. The
number of training events should be selected based on the computa­
tional budget allowed for setting up the surrogate model. The compu­
tational budget depends on the timeframe for the project and the
computational demand of the high-fidelity model. The aim is that the
training events span the range of flooding behaviours exhibited

2.2.2. Case studies
A LSG surrogate model is set up for three case studies, namely the
town of Carlisle in the United Kingdom, the Burnett River catchment in
Australia, and the Echuca-Moama town and floodplain area in Australia.
The locations and general topographies of the case studies are shown in
Fig. 5. The details of each case study are given in the following sections.

2.2.2.1. Carlisle. The Carlisle case study is located in the central part of
the United Kingdom and is an urban area with the River Eden, River
Caldew, and River Petteril running through. The Carlisle case study has
previously been used by Fraehr et al. (2024); Neal et al. (2013); Parkes
et al. (2013) and Kabir et al. (2020) and provides a challenging appli­
cation for flood inundation modelling, due to the flat topography and

Fig. 4. Development of surrogate model using LESS.

6

### Page 7

N. Fraehr et al.
Journal of Environmental Management 373 (2025) 123570

Fig. 5. Location and elevation of case studies. Panels a and b show the location of the case studies in the United Kingdom and Australia, respectively. Panel c, d, and e
show the outline of the model domains and elevations for the Carlisle, Burnett River, and Echuca-Moama case studies. Basemaps are from OpenStreetMap (2024).

confluence of the three rivers making the area prone to fluvial flooding.

for these historical events are published in the dataset by Fraehr (2024).
For training of the surrogate model, candidate events are generated by
scaling each of the boundary conditions for the 9 available historical
events by a factor of 0.5, 1.0, 1.5, and 2.0. There are three boundary
conditions in the Carlisle case study, and following equation (1), this
procedure results in 576 events (64 versions of each historical event). In

#### 2005 a flood event caused significant flooding in Carlisle (Kabir et al.,

2020), and therefore the 64 versions of this event are used for validation.
The remaining 512 events are candidate events, whereof the specific
events used for training are selected using LESS as described in Section
2.1. The boundary conditions for the original historic events and the
scaled candidate events can be seen in Appendix A, Figure A.1.

The high-fidelity model for the Carlisle case study is developed using
LISFLOOD-FP (Bates and De Roo, 2000) and covers a domain of 14.5
km2. Flood inundation is simulated on a 5 m × 5 m quadratic grid with a
Manning’s n of 0.055 s/m1/3, resulting in 581,061 cells in total. A
low-fidelity model for this case study is developed using HEC-RAS (US
Army Corps of Engineers, 2024), which is available from the previous
study by Fraehr et al. (2024). The low-fidelity model simulates flood
inundation on an unstructured grid with 5681 grid cells. The low-fidelity
model includes the same model domain, boundary conditions, topog­
raphy, and Manning’s n as the high-fidelity model.

In the study by Fraehr et al. (2024), the high-fidelity model is used to
simulate 9 historical events lasting hours to days. The simulation results

7

### Page 8

N. Fraehr et al.
Journal of Environmental Management 373 (2025) 123570

2.2.2.2. Burnett River. The Burnett River case study is located near the
coast in Queensland, Australia, and has previously been used by Fraehr
et al. (2023b); Zhou et al. (2021) and Fraehr et al. (2024). The Burnett
River case study has a steep topography with 15 boundary conditions
(14 inflows and 1 water level boundary condition), whereof the Burnett
River and the downstream sea water level are the main flood drivers.

inundation candidate events (See Sections 2.1.1 and 2.1.3), (III) historic
events and the full set of candidate events (See Sections 2.1.1 and 2.1.2),
and (IV) events selected using LESS (See Sections 2.1.1 to 2.1.4). The
accuracy of surrogate models generally improves with an increase in
training data, thus training the surrogate model using historic events
and the full set of candidate events (III) is a reference of how high an
accuracy can be achieved using the highest computational budget to
generate training data using a high-fidelity model. Comparing to (III)
provides insight into the potential computational advantages of using
LESS (IV). For the Echuca-Moama case study, it was not possible to train
the LSG model using the historic events and the full set of candidate
events (III) due to the prohibitively high computational costs involved in
running the high-fidelity model. It is chosen to select a maximum of 10
events using LESS in addition to the available historic events and
maximum inundation candidate events. This number of events is
considered to provide a reasonable balance between model accuracy and
the computational burden involved in running the high-fidelity.

In the Burnett River case study, the high-fidelity model is developed
using TUFLOW (Huxley and Syme, 2016). The high-fidelity model
simulates flooding using 3,697,597 quadratic grid cells of 20 m × 20 m
covering a model domain of 1479 km2. The roughness varies within the
model domain, described by Manning’s n ranging from 0.02 s/m1/3 to

#### 0.15 s/m1/3. The low-fidelity model is developed using HEC-RAS (US

Army Corps of Engineers, 2024) by Fraehr et al. (2023b). The
low-fidelity model has 15,256 unstructured grid cells but otherwise in­
cludes the same information regarding topography and boundary con­
ditions as the high-fidelity model.

The high-fidelity model has been used to simulate a total of 74 events
by Zhou et al. (2021), which are available in the dataset by Fraehr
(2024). These 74 events range from days to weeks in duration and have
been generated from an original 3 historical and 1 design events through
scaling of the inflow boundary conditions to return periods ranging from

#### 2 to 500 years in the Burnett River and by using high/low downstream

sea level conditions developed in the Regional Ocean Modelling System
(ROMS) (Shchepetkin and McWilliams, 2005). These scaling procedures
resulted in 18 versions of the 1971 original historical event which are
used for validation. The remaining 56 events are candidate events. The
boundary conditions for the Burnett River and downstream sea level for
all the training and validation events are shown in Appendix A,
Figure A.2.

The accuracy of the developed surrogate models is assessed by
comparing the predicted flood inundation by the surrogate models to
high-fidelity simulations. The maximum inundation extent is evaluated
using the Critical Success Index (CSI), the peak water depth using the
Average Peak Difference (Δymax), and water depth hydrographs in each
cell using the Average Root Mean Square Error (RMSE), see equations
(4)–(6) (Fraehr et al., 2024; Schaefer, 1990):


#### CSI =

TP

#### TP + FN + FP

(4)

∑
N

Δymax = 1

ymax(n) −̂ ymax(n)
(5)

N

n=1

2.2.2.3. Echuca-Moama. The Echuca-Moama case study is located on
the border between New South Wales and Victoria in Australia. The area
is highly prone to flooding as a result of the confluence of the Murray
River, Campaspe River, and Goulburn River in a flat topography. Severe
flooding can arise from any one or a combination of the three rivers, and
the flood events can last for weeks to months as a result of the large
upstream contributing areas and the low gradients of the rivers.

√
√
√
√
(6)

∑
N

∑
T


#### RMSE = 1


1
T

(̂y(t, n) −y(t, n))2

N

n=1̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅̅

t=1

where TP is the area that has been correctly predicted as flooded, FN is
the area that has been falsely predicted as dry, FP is the area that has
been falsely predicted as flooded, N is the number of grid cells in the
models, ymax is the peak water depth simulated in the high-fidelity
model, ̂ymax is the peak water depth predicted by the surrogate model,
and T is the number of timesteps in the flood event. CSI equal to 1, Δymax
equal to 0, and RMSE equal to 0 are considered perfect predictions.

A high-fidelity model has been developed by Water Technology
(2024) using TUFLOW (Huxley and Syme, 2016). The high-fidelity
model includes 4,377,862 quadratic cells of 20 m × 20 m. The model
covers an area of 1750 km2, has three inflow boundary conditions (i.e.
one for each river), and a spatially varying Manning’s n roughness be­
tween 0.02 s/m1/3 and 0.35 s/m1/3. The low-fidelity model is developed
using HEC-RAS (US Army Corps of Engineers, 2024) following the
procedure outlined in Fraehr et al. (2023b). The low-fidelity model has
an unstructured grid with a total of 16,680 cells.

3. Results

The performance of the trained LSG surrogate models for all three
study areas is summarised in Table 1. For the Carlisle and Burnett River
case studies, the results are shown as the mean (standard deviation) of
all scaled versions of the 2005 and 1974 validation events. The results
for the Echuca-Moama case study are for the historic 2022 validation
event.

For the Echuca-Moama case study, 4 historical events are available.
Due to the computational demand of running the high-fidelity TUFLOW
model for this case study, only one event is used for validation. The
validation event is the 2022 flood event that resulted in significant
inundation for large parts of the Echuca-Moama area. Candidate events
for LESS are generated from the remaining three historical events
through scaling of the inflow boundary conditions, see Appendix A,
Figure A.3. After examining the behaviours of historical events, the in­
flows were scaled independently up to magnitudes corresponding to a
500-year return period (Water Technology, 2024) using scaling factors
of 0.5–7.0 with a 0.5 incremental interval. This procedure generated
boundary conditions for a total of 780 candidate events.

Training the LSG model using only the available historic events (I)
yielded the lowest accuracy results in all three case studies. This is ex­
pected, as this model is trained using the lowest number of training
events. Training LSG models using both the historic and the subset of
maximum inundation candidate events (II) show increased accuracy
compared to the LSG model trained only on historic events (I). This
demonstrates that the accuracy of the surrogate model can be signifi­
cantly improved by including only a few additional large flood events,
which is consistent with the results reported by Fraehr et al. (2024).

2.3. Performance evaluation

The LSG models trained using historical and the full set of candidate
events (III) exhibit the highest accuracy of all the different LSG models
due to the high number of training events included. However, the LSG
models trained based on the events selected using LESS (IV) show almost
equally accurate predictions to the LSG model trained using historical
and the full set of candidate events (III). This demonstrates the value of

To evaluate the performance of surrogate models trained based on
events selected using LESS, we train surrogate models using four
different groups of datasets comprising: (I) available historic events (See
Section 2.1.1), (II) historic events and the subset of maximum

8

### Page 9

N. Fraehr et al.
Journal of Environmental Management 373 (2025) 123570

behaviours included in the available historic events and generated
candidate events.

Table 1
Accuracy of LSG models training on original historic events (I), historic events
and the subset of maximum inundation candidate events (II), historic events and
the full set candidate events (III), and events selected using LESS (IV).

The performance of the LSG models developed using an increasing
number of training events is shown in Fig. 7. The number of training
events used differs between case studies due to the different number of
available historic events and generated candidate events. The surrogate
models are either trained using historic events (Hist, I), historic and the
subset of maximum inundation candidate events (Hist + Max Inun., II),
historic and the full set of candidate events (Hist + All Cand., III), or
events selected using LESS (IV). It is evident from the metrics shown in
Fig. 7 (CSI, average peak difference, and average RMSE) that the accu­
racy of the LSG models generally improves as the number of training
events increases. It is noticeable that only minor improvements are
achieved by including the full set the candidate events for training (III),
and this is the case for all case studies. In fact, after selecting less than 10
events using the iterative selection strategy in LESS (See Section 2.1.4),
the values of the performance metrics stabilise. This illustrates the ef­
ficacy of LESS in ranking and selecting a small number of candidate
events to represent a comprehensive range of flooding behaviours to be
included in the training of the surrogate model.

Number of
training
events


#### CSI [-]

Average peak
difference [m]

Average
RMSE [m]

Carlisle
(I) Historic only
8
0.91
(0.04)


#### 0.16 (0.21)


#### 0.16 (0.05)


(II) Historic +

10
0.94
(0.04)


#### 0.02 (0.03)


#### 0.13 (0.04)


Max inundation

(III) Historic + All

512
0.97
(0.03)


#### 0.00 (0.02)


#### 0.09 (0.03)


candidates*


#### (IV) LESS

20
0.96
(0.03)

−0.01 (0.02)

#### 0.11 (0.04)


Burnett River
(I) Historic only
2
0.78
(0.19)

−0.09 (0.23)

#### 0.60 (0.22)


(II) Historic +

3
0.86
(0.10)

−0.06 (0.06)

#### 0.52 (0.17)


Max inundation

(III) Historic + All

56
0.96
(0.03)


#### 0.00 (0.05)


#### 0.22 (0.04)


candidates

Table 2 shows the computational costs of using LESS compered to
simulating the full set of candidate events using the high-fidelity model.
The models are run on a high-performance computer with Intel® Xeon®
E−2288G CPU, 64 GB RAM, 64 cores, and an NVIDIA Quadro RTX 5000
graphic card. The selection of events using LESS is programmed in Py­
thon. In the Echuca-Moama case study, several computing setups have
been used to reduce the computational costs, and only the events
selected using LESS have been run using the high-fidelity model. The
high-fidelity model times shown are estimated based on the average
event simulation times for the events run on the same HPC computing
setup as for the Carlise and Burnett River case studies. The computa­
tional costs vary between case studies, as each case study has different
sizes, number and duration of candidate events, and different high-
fidelity models (See Section 2.2.2). For the three case studies used in
this study, the use of LESS results in computational savings of 76%–97%,
highlighting that by reducing the number of events to simulate using the
high-fidelity model, LESS significantly reduces the computational costs
of generating training data for the surrogate model.


#### (IV) LESS

13
0.94
(0.05)

−0.01 (0.05)

#### 0.23 (0.03)


Echuca-Moama
(I) Historic only
3
0.63
0.22
0.19
(II) Historic +

10
0.80
0.05
0.14

Max inundation

(III) Historic + All

–
–
–
–

candidates


#### (IV) LESS

20
0.88
0.02
0.13

*The Gaussian Process model within the LSG model was trained using every 10th
timestep due to memory issues.

LESS in selecting a small number of events that are representative of the
full set of candidate events, and thus, results in robust training of the
surrogate model.

To further evaluate the performance of the LSG models trained based
on events selected using LESS (IV) and those trained using the available
historic and full set of candidate events (III), the maximum inundation
depths are compared to the high-fidelity model in Fig. 6.Fig. 6 shows the
comparison results of the 2005 historic event for the Carlisle case study,
the 1979 historic event for the Burnett River case study, and the 2022
historic event for the Echuca-Moama case study. As can be seen in the
figure, the predictions obtained using the LSG models trained using the
two groups of training data (III and IV) are similar and there are no clear
differences in the predictions of the maximum water depths. In the
Carlisle and Burnett River case studies the differences in maximum
water depths are less than 25 cm for the majority of the model domains,
indicating a good level of agreement between the high-fidelity and LSG
models.

4. Discussion

The results demonstrate the potential of LESS in ensuring robust
training of a surrogate flood inundation model using only a small
number of training events. The LSG surrogate models trained based on
events selected using LESS (IV) show high accuracy and have very
similar performance to the LSG surrogate models trained using available
historic events and the full set of candidate events (III). This result is
consistent across all three case studies, illustrating the approach is not
constrained to a single case study.

The LSG model trained based on events selected using LESS (IV) in
the Echuca-Moama case study generally yields differences in water
depths of less than 25 cm, but it underpredicts water depths in the
eastern region of the domain (green areas), and overpredicts in the
central parts of the domain (red and orange areas). The reason for these
discrepancies between the high-fidelity and LSG models in the Echuca-
Moama case study may be due to several reasons. First, flooding
behaviour in the Echuca-Moama case study is very complex as it in­
volves the interaction between three dominant inflows over a very flat
terrain. The red and orange areas are primarily located in and around a
large depression. In the high-fidelity model, this depression is protected
via levees, but in the low-fidelity model, the coarse resolution di­
minishes the impact of the levees. Local adaptations of the computa­
tional grid could potentially address this issue, but that falls outside the
scope of this study. Second, the 2022 historic event was unlike any prior
event in the historical record in terms of the timing and magnitude of the
inflows (Water Technology, 2024). Consequently, this flow behaviour
may not have been properly represented by the range of flooding

LESS relies on the use of a low-fidelity model to provide estimates for
the set of candidate events. While running a low-fidelity model for
hundreds to thousands of candidate events has the potential to be
computationally impractical, if suitable care is taken when developing a
coarse model then this should not be a problem. For all three case studies
used in this study, the low-fidelity model run time is minimal in the
overall computational scheme (See Table 2). The largest number of
candidate events is used in the Echuca-Moama case study where a total
of 780 candidate events are simulated, and this took less than two days
of elapsed time to run using a high-performance computer with Intel®
Xeon® E−2288G CPU, 64 GB ram, 64 cores, and an NVIDIA Quadro RTX

#### 5000 graphic card. In comparison, the high-fidelity model takes

approximately the same time to simulate a single flood event in the
Echuca-Moama case study. Considering the alternative of randomly
selecting training events and potentially running the high-fidelity model
for flood events that only include a small range of flooding behaviours,
the computational costs involved in applying LESS are insignificant.

9

### Page 10

N. Fraehr et al.
Journal of Environmental Management 373 (2025) 123570

Fig. 6. Comparing the maximum water depth simulated using the high-fidelity model to predictions made using the LSG surrogate model trained with events selected
using LESS (IV) and trained using historic and the full set of candidate events (Hist + All. Cand., III), respectively. Basemaps are from OpenStreetMap (2024).

Another important aspect of LESS is the generation of the candidate
events. The candidate events can be generated in different ways as
shown in the three case studies used in this study. It is important the
candidate events are physically realistic in terms of the duration, rise
and fall of the main flood drivers, and the interdependence between all

system inputs. In the initial work of this study, we carried out tests using
synthetic hydrographs generated stochastically using a mathematical
function, Equation (56) in Fenton (2019). Although the magnitude of the
inflows was similar to the historic ones and LESS could identify the
significant candidate events, the use of synthetic hydrographs resulted

10

### Page 11

N. Fraehr et al.
Journal of Environmental Management 373 (2025) 123570

Fig. 7. The impact of the number of training events (Shown in parentheses in the bottom three rows for each case study) on the accuracy of the surrogate model.
Results are shown as a mean value with error bars for the maximum and minimum values of all the predicted validation events.

events as candidate events, though it is acknowledged that such an
approach is not well suited to capturing flood behaviours that are unlike
anything found in the historic record.

Table 2
Computational costs of generating training data by simulating all candidate
events using the high-fidelity model compared to using LESS, where only a
selected number of training events is simulated using the high-fidelity model.
The number of events simulated is seen in Table 1.

LESS explicitly selects the maximum inundation candidate events to
be included as training events. However, if this step of LESS is excluded,
the same events would most likely still be selected via the iterative se­
lection process using EOF analysis, as the maximum inundation candi­
date events would exhibit significant flooding behaviour that would
cause them to be selected. By excluding the step of explicitly selecting
the maximum inundation candidate events from LESS, the approach
would be simplified, but there is also a risk that all areas likely to be
flooded are not included in the training data. In addition, the maximum
inundation candidate events act as a robust initialisation of the iterative
candidate event selection process in Section 2.1.4.

Computational
process

Carlisle
Burnett
River

Echuca-
Moama

(III) Historic + All
candidates

High-fidelity
model

699.85
h


#### 909.54 h

47,710.87 h


#### (IV) LESS

High-fidelity
model


#### 21.31 h


#### 217.71 h


#### 1223.36 h


Low-fidelity
model


#### 3.64 h


#### 0.08 h


#### 32.74 h


LESS event
selection


#### 0.13 h


#### 0.01 h


#### 0.19 h


When applying LESS, the number of training events to select using
the approach has to be decided beforehand. In general, the number of
training events should be selected according to the available computa­
tional budget. However, another option is to identify when including
additional events will not improve model performance and use this as a
stopping criterion. Developing such a stopping criterion is beyond the
scope of this paper. However, one potential approach is using a

Computational savings using LESS

#### 96.42 %


#### 76.05 %


#### 97.37 %


in poor performance of the surrogate model when used to predict his­
toric events as they represented combinations of flood drivers that were
not physically realistic. Unless a special effort is taken to ensure that
such synthetic hydrographs correctly capture the dependencies in a
physically realistic manner, it is simpler to use scaled versions of historic

11

### Page 12

N. Fraehr et al.
Journal of Environmental Management 373 (2025) 123570

similarity metric based on the EOF analysis, similar to the iterative se­
lection described in Section 2.1.4. The use of a similarity metric between
training events and new events could also be advantageous for real-time
applications. A quantitative assessment of the similarity in flooding
behaviours of an event unfolding in real time with training events used
to develop the model could be used to help assess the level of confidence
in the forecasts.

Although LESS selects the most informative candidate events for
training, the accuracy of the developed surrogate models is still
dependent on whether the selected events are physically realistic, and
which could plausibly occur in the case study. The accuracy of the
surrogate model generally increases with the number of training events
selected, where the number of events selected must be specified by the
user. Consequently, the number of training events selected should be
sufficient to ensure a good model performance, but not be larger than
needed, as this would unnecessarily increase computational costs.
Future studies should consider the development of a stopping criterion
to ensure that a sufficient number of training events is selected to pro­
vide robust training of the surrogate model. Such a stopping criterion
could simplify the use of LESS.

In this study, LESS is used in the development of surrogate models for
modelling flood inundation. Although LESS is tested using the LSG
surrogate model, LESS should also be useful for other surrogate flood
inundation models. This is because LESS selects training events based on
the inundation behaviour exhibited during the flood events, meaning
the surrogate model type, setup, or structure does not affect the selection
process. In addition, LESS could also be applied when developing sur­
rogate models in other fields and applications where the spatio-temporal
information, timing, and/or hysteresis of the training data are of
importance for the surrogate model training. This could be in fields such
as groundwater modelling (Gholizadeh et al., 2023; Previati and Crosta,
2024), storm surge and stormwater modelling (Khatooni et al., 2023; Ma
et al., 2019; Sahoo et al., 2021), water quality (Rahat et al., 2023),
oceanography (Huang et al., 2022; van der Merwe et al., 2007), and
parameter optimisation (Coppede et al., 2019).

This study has focused on developing LESS for selecting training
events for surrogate models used in flood inundation modelling. How­
ever, surrogate models are used for many different applications. For that
reason, LESS should be tested for new case studies and in other fields to
explore the value of the approach in more detail.

CRediT authorship contribution statement

Niels Fraehr: Writing – review & editing, Writing – original draft,
Visualization, Validation, Software, Methodology, Investigation, Formal
analysis, Data curation, Conceptualization. Quan J. Wang: Writing –
review & editing, Writing – original draft, Supervision, Resources,
Project administration, Conceptualization. Wenyan Wu: Writing – re­
view & editing, Writing – original draft, Supervision, Conceptualization.
Rory Nathan: Writing – review & editing, Writing – original draft, Su­
pervision, Conceptualization.

5. Conclusion

This study introduces a novel approach - Low-fidelity and EOF
analysis Sampling Strategy (LESS) - for selecting training events to run
using a high-fidelity model for surrogate model development. LESS
utilises a low-fidelity model to simulate a set of candidate events, ranks
the candidate events and selects a subset of events to ensure that a wide
range of flooding behaviours is included in the training data. The
approach is based on objective criteria and provides insight into the
events selected for training, thus avoiding the use of trial-and-error
approaches or subjective choices of individual model developers. LESS
reduces the computational costs of using the high-fidelity model to
generate flood data for a large number of training events, as only the
most informative events are selected for training of the surrogate model.

Declaration of competing interest

The authors declare that they have no known competing financial
interests or personal relationships that could have appeared to influence
the work reported in this paper.

The effectiveness of LESS is demonstrated using the LSG surrogate
model applied to three case studies in the United Kingdom and Australia.
LESS ensures robust training of the LSG model to allow for accurate
predictions in all three case studies using only a small number of training
events. The LSG models trained using events selected via LESS (13–20
events, RMSE <0.23 m) show similar performance to the LSG models
trained using historical and the full set of candidate events (56–780
events, RMSE <0.22 m), even though the number of training events is
significantly lower. The lower number of training events also effectively
reduces the computational costs by 76%–97%.


#### Acknowledgments


Niels Fraehr acknowledges support from The University of Mel­
bourne via the Melbourne Research Scholarship, and Wenyan Wu ac­
knowledges support from the Australian Research Council via the
Discovery Early Career Researcher Award (DE210100117). We
acknowledge Water Technology, as well as the Murray River Council
and the Campaspe Shire Council for providing a TUFLOW model for the
Echuca-Moama case study. We also acknowledge BMT for providing a
TUFLOW license to conduct the TUFLOW simulations.


#### Appendix A. Historic and scaled boundary conditions for case studies


12

### Page 13

N. Fraehr et al.
Journal of Environmental Management 373 (2025) 123570

Fig. A.1. Inflow boundary conditions in the Carlisle case study. Black lines are the original boundary conditions for the available historic events, and grey lines are
the scaled boundary conditions to generate candidate events. All boundary conditions for all events are scaled by factors 0.5, 1.0, 1.5, and 2.0. *Event used
for validation.

Fig. A.2. Inflow and water level boundary conditions in the Burnett River case study. In total, the Burnett River case study has 14 inflow boundaries, but the Burnett
River (i.e. outflow from Paradise Dam) is the main flood driver. Black lines are the original boundary conditions for the available historic events, and grey lines are
the scaled boundary conditions to generate candidate events. The inflow is scaled to return periods ranging from 2 to 500 years with a low and high downstream
water level following Zhou et al. (2021). *Event used for validation.

13

### Page 14

N. Fraehr et al.
Journal of Environmental Management 373 (2025) 123570

Fig. A.3. Inflow boundary conditions in the Echuca-Moama case study. Black lines are the original boundary conditions for the available historic events, and grey
lines are the scaled boundary conditions to generate candidate events. Each inflow is scaled to magnitudes corresponding to a 500-year return period using scaling
factors of 0.5–7.0 with a 0.5 incremental interval. *Event used for validation.

Data availability

surface method. Appl. Ocean Res. 90 (11). https://doi.org/10.1016/j.
apor.2019.05.026. Article 101841.
DHI, 2019. Mike flood. Retrieved 29-11-2021 from. https://manuals.mikepoweredbydhi.

Data will be made available on request.

help/2019/Water_Resources/MIKE_FLOOD_UserManual.pdf.
Donnelly, J., Abolfathi, S., Pearson, J., Chatrabgoun, O., Daneshkhah, A., 2022. Gaussian

process emulation of spatio-temporal outputs of a 2D inland flood model. Water Res.
225, 119100. https://doi.org/10.1016/j.watres.2022.119100.
Donnelly, J., Daneshkhah, A., Abolfathi, S., 2024. Physics-informed neural networks as


#### References


Aires, F., Papa, F., Prigent, C., Cretaux, J.F., Muriel, B.N., 2014. Characterization and

surrogate models of hydrodynamic simulators. Sci. Total Environ. 912, 168814.
https://doi.org/10.1016/j.scitotenv.2023.168814.
Fauzi, A., Mizutani, N., 2020. Machine learning algorithms for real-time tsunami

space-time downscaling of the inundation extent over the inner Niger delta using
GIEMS and MODIS data. J. Hydrometeorol. 15 (1), 171–192.
Aires, F., Venot, J.P., Massuel, S., Gratiot, N.P., D, B., Prigent, C., 2020. Surface water

inundation forecasting: a case study in Nankai region [article]. Pure Appl. Geophys.

#### 177 (3), 1437–1450. https://doi.org/10.1007/s00024-019-02364-4.

Fenton, J.D., 2019. Flood routing methods. J. Hydrol. 570, 251–264. https://doi.org/

evolution (2001-2017) at the Cambodia/vietnam border in the upper mekong delta
using satellite MODIS observations. Rem. Sens. 12 (5), 19. https://doi.org/10.3390/
rs12050800. Article 800.
Asher, M.J., Croke, B.F.W., Jakeman, A.J., Peeters, L.J.M., 2015. A review of surrogate

10.1016/j.jhydrol.2019.01.006.
Fraehr, N., 2024. Surrogate Flood Model Comparison - Datasets and python Code

models and their application to groundwater modeling. Water Resour. Res. 51 (8),
5957–5973. https://doi.org/10.1002/2015wr016967.
Bates, P.D., 2022. Flood inundation prediction. Annu. Rev. Fluid Mech. 54 (1), 287–315.

(Version 1), The University of Melbourne.
Fraehr, N., Wang, Q.J., Wu, W., Nathan, R., 2022. Upskilling low-fidelity hydrodynamic

models of flood inundation through spatial analysis and Gaussian Process learning.
Water Resour. Res. 58 (8), e2022WR032248. https://doi.org/10.1029/

#### 2022WR032248.

Fraehr, N., Wang, Q.J., Wu, W., Nathan, R., 2023a. Development of a fast and accurate

https://doi.org/10.1146/annurev-fluid-030121-113138.
Bates, P.D., De Roo, A.P.J., 2000. A simple raster-based model for flood inundation

simulation. J. Hydrol. 236 (1–2), 54–77. https://doi.org/10.1016/s0022-1694(00)
00278-x.
Bentivoglio, R., Isufi, E., Jonkman, S.N., Taormina, R., 2022. Deep learning methods for

hybrid model for floodplain inundation simulations. Water Resour. Res. 59 (6),
e2022WR033836. https://doi.org/10.1029/2022WR033836.
Fraehr, N., Wang, Q.J., Wu, W., Nathan, R., 2023b. Supercharging hydrodynamic

flood mapping: a review of existing applications and future research directions.
Hydrol. Earth Syst. Sci. 26 (16), 4345–4378. https://doi.org/10.5194/hess-26-4345-
2022.
Bentivoglio, R., Isufi, E., Jonkman, S.N., Taormina, R., 2023. Rapid spatio-temporal flood

inundation models for instant flood insight. Nature Water 1 (10), 835–843. https://
doi.org/10.1038/s44221-023-00132-2.
Fraehr, N., Wang, Q.J., Wu, W., Nathan, R., 2024. Assessment of surrogate models for

modelling via hydraulics-based graph neural networks. Hydrol. Earth Syst. Sci. 27
(23), 4227–4246. https://doi.org/10.5194/hess-27-4227-2023.
Bermudez, M., Ntegeka, V., Wolfs, V., Willens, P., 2018. Development and comparison of

flood inundation: the physics-guided LSG model vs. state-of-the-art machine learning
models. Water Res. 252, 121202. https://doi.org/10.1016/j.watres.2024.121202.
Gholizadeh, H., Zhang, Y., Frame, J., Gu, X., Green, C.T., 2023. Long short-term memory

two fast surrogate models for urban pluvial flood simulations. Water Resour. Manag.

#### 32 (8), 2801–2815. https://doi.org/10.1007/s11269-018-1959-8.

Chang, C.-H., Lee, H., Do, S.K., Du, T.L.T., Markert, K., Hossain, F., Ahmad, S.K.,

models to quantify long-term evolution of streamflow discharge and groundwater
depth in Alabama. Sci. Total Environ. 901, 165884. https://doi.org/10.1016/j.
scitotenv.2023.165884.
Guha-Sapir, D., Below, R., Hoyois, P., 2024. EM-DAT: the CRED/OFDA International

Piman, T., Meechaiya, C., Bui, D.D., Bolten, J.D., Hwang, E., Jung, H.C., 2023.
Operational forecasting inundation extents using REOF analysis (FIER) over lower
Mekong and its potential economic impact on agriculture. Environ. Model. Software
162, 105643. https://doi.org/10.1016/j.envsoft.2023.105643.
Chang, L.-C., Liou, J.-Y., Chang, F.-J., 2022. Spatial-temporal flood inundation nowcasts

Disaster Database ([Database]. Universit´e Catholique de Louvain, Brussels, Belgium.
www.emdat.be.
Hannachi, A., Jolliffe, I.T., Stephenson, D.B., 2007. Empirical orthogonal functions and

related techniques in atmospheric science: a review. Int. J. Climatol. 27 (9),
1119–1152. https://doi.org/10.1002/joc.1499.
He, J., Zhang, L., Xiao, T., Wang, H., Luo, H., 2023. Deep learning enables super-

by fusing machine learning methods and principal component analysis. J. Hydrol.
612, 128086. https://doi.org/10.1016/j.jhydrol.2022.128086.
Chu, H.B., Wu, W.Y., Wang, Q.J., Nathan, R., Wei, J.H., 2020. An ANN-based emulation

resolution hydrodynamic flooding process modeling under spatiotemporally varying
rainstorms. Water Res. 239, 120057. https://doi.org/10.1016/j.
watres.2023.120057.
Huang, L.M., Jing, Y., Chen, H.Y., Zhang, L., Liu, Y.L., 2022. A regional wind wave

modelling framework for flood inundation modelling: application, challenges and
future directions. Environ. Model. Software 124, 17. https://doi.org/10.1016/j.
envsoft.2019.104587. Article 104587.
Contreras, M.T., Gironas, J., Escauriaza, C., 2020. Forecasting flood hazards in real time:

prediction surrogate model based on CNN deep learning network. Appl. Ocean Res.
126. https://doi.org/10.1016/j.apor.2022.103287. Article 103287.
Huxley, C., Syme, B., 2016. Tuflow GPU – best practice advice for hydrologic and

a surrogate model for hydrometeorological events in an Andean watershed. Nat.
Hazards Earth Syst. Sci. 20 (12), 3261–3277. https://doi.org/10.5194/nhess-20-
3261-2020.
Coppede, A., Gaggero, S., Vernengo, G., Villa, D., 2019. Hydrodynamic shape

hydraulic model simulations hydrology and water resources symposium 2016.
Queenstown (Huxley).

optimization by high fidelity CFD solver and Gaussian process based response

14

### Page 15

N. Fraehr et al.
Journal of Environmental Management 373 (2025) 123570

IPCC, 2021. Climate Change 2021: the Physical Science Basis. Contribution of Working

Rahat, S.H., Steissberg, T., Chang, W., Chen, X., Mandavya, G., Tracy, J., Wasti, A.,

Group I to the Sixth Assessment Report of the Intergovernmental Panel on Climate
Change. Cambridge University Press. https://doi.org/10.1017/9781009157896 (in
press).
Jam-Jalloh, S.U., Liu, J., Wang, Y.C., Li, Z.J., Jabati, N.M.S., 2023. Wavelet analysis and

Atreya, G., Saki, S., Bhuiyan, M.A.E., Ray, P., 2023. Remote sensing-enabled
machine learning for river water quality modeling under multidimensional
uncertainty. Sci. Total Environ. 898, 165504. https://doi.org/10.1016/j.
scitotenv.2023.165504.
Razavi, S., Tolson, B.A., Burn, D.H., 2012. Review of surrogate modeling in water

the information cost function Index for selection of calibration events for flood
simulation. Water 15 (11). https://doi.org/10.3390/w15112035. Article 2035.
Jolliffe, I.T., Cadima, J., 2016. Principal component analysis: a review and recent

resources. Water Resour. Res. 48 (7). https://doi.org/10.1029/2011WR011527.
Sahoo, A., Samantaray, S., Ghose, D.K., 2021. Prediction of flood in barak river using

developments. Phil. Trans. Math. Phys. Eng. Sci. 374 (2065), 20150202. https://doi.
org/10.1098/rsta.2015.0202.
Kabir, S., Patidar, S., Xia, X.L., Liang, Q.H., Neal, J., Pender, G., 2020. A deep

hybrid machine learning approaches: a case study [article]. J. Geol. Soc. India 97
(2), 186–198. https://doi.org/10.1007/s12594-021-1650-1.
Santiago-Collazo, F.L., Bilskie, M.V., Hagen, S.C., 2019. A comprehensive review of

convolutional neural network model for rapid prediction of fluvial flood inundation.
J. Hydrol. 590 (16), 125481. https://doi.org/10.1016/j.jhydrol.2020.125481.
Kaiser, H.F., 1960. The application of electronic computers to factor analysis. Educ.

compound inundation models in low-gradient coastal watersheds. Environ. Model.
Software 119, 166–181. https://doi.org/10.1016/j.envsoft.2019.06.002.
Schaefer, J.T., 1990. The critical success Index as an indicator of warning skill. Weather

Psychol. Meas. 20 (1), 141–151. https://doi.org/10.1177/001316446002000116.
Karim, F., Armin, M.A., Ahmedt-Aristizabal, D., Tychsen-Smith, L., Petersson, L., 2023.

Forecast. 5 (4), 570–575. https://doi.org/10.1175/1520-0434(1990)005<0570:
Tcsiaa>2.0.Co, 2.
Shchepetkin, A.F., McWilliams, J.C., 2005. The regional oceanic modeling system

A review of hydrodynamic and machine learning approaches for flood inundation
modeling. Water 15 (3). https://doi.org/10.3390/w15030566. Article 566.
Khatooni, K., Hooshyaripor, F., MalekMohammadi, B., Noori, R., 2023. A combined

(ROMS): a split-explicit, free-surface, topography-following-coordinate oceanic
model. Ocean Model. 9 (4), 347–404. https://doi.org/10.1016/j.
ocemod.2004.08.002.
Sun, S., Bertrand-Krajewski, J.-L., 2012. On calibration data selection: the case of

qualitative–quantitative fuzzy method for urban flood resilience assessment in Karaj
City, Iran. Sci. Rep. 13 (1), 241. https://doi.org/10.1038/s41598-023-27377-x.
Liao, Y., Wang, Z., Chen, X., Lai, C., 2023. Fast simulation and prediction of urban pluvial

stormwater quality regression models. Environ. Model. Software 35, 61–73. https://
doi.org/10.1016/j.envsoft.2012.02.007.
Tellman, B., Sullivan, J.A., Kuhn, C., Kettner, A.J., Doyle, C.S., Brakenridge, G.R.,

floods using a deep convolutional neural network model. J. Hydrol. 624, 129945.
https://doi.org/10.1016/j.jhydrol.2023.129945.
Lin, Q., Leandro, J., Gerber, S., Disse, M., 2020. Multistep flood inundation forecasts with

Erickson, T.A., Slayback, D.A., 2021. Satellite imaging reveals increased proportion
of population exposed to floods. Nature 596 (7870), 80–86. https://doi.org/
10.1038/s41586-021-03695-w.
Teng, J., Jakeman, A.J., Vaze, J., Croke, B.F.W., Dutta, D., Kim, S., 2017. Flood

resilient backpropagation neural networks: kulmbach case study [article]. Water 12
(12), 20. https://doi.org/10.3390/w12123568. Article 3568.
Ma, P., Konomi, G.K.B.A., Asher, T.G., Toro, G.R., Cox, A.T., 2019. Multifidelity

computer model emulation with high-dimensional output: an application to storm
surge. arXiv. https://doi.org/10.48550/ARXIV.1909.01836.
Maier, H.R., Galelli, S., Razavi, S., Castelletti, A., Rizzoli, A., Athanasiadis, I.N., S`anchez-

inundation modelling: a review of methods, recent advances and uncertainty
analysis. Environ. Model. Software 90, 201–216. https://doi.org/10.1016/j.
envsoft.2017.01.006.
TUFLOW, 2020. TUFLOW Classic and HPC - 2020-01 Release Notes [TUFLOW Sub-

Marr`e, M., Acutis, M., Wu, W., Humphrey, G.B., 2023a. Exploding the myths: an
introduction to artificial neural networks for prediction and forecasting. Environ.
Model. Software 167, 105776. https://doi.org/10.1016/j.envsoft.2023.105776.
Maier, H.R., Zheng, F., Gupta, H., Chen, J., Mai, J., Savic, D., Loritz, R., Wu, W., Guo, D.,

subgrid Sampling Documentation].
US Army Corps of Engineers, 2024. HEC-RAS 2D user’s manual [computer program

documentation](HEC-RAS - river analysis system, version 6.4). https://www.hec.usa
ce.army.mil/confluence/rasdocs/r2dum/latest.
van der Merwe, R., Leen, T.K., Lu, Z.D., Frolov, S., Baptista, A.M., 2007. Fast neural

Bennett, A., Jakeman, A., Razavi, S., Zhao, J., 2023b. On how data are partitioned in
model development and evaluation: confronting the elephant in the room to enhance
model generalization. Environ. Model. Software 167, 105779. https://doi.org/
10.1016/j.envsoft.2023.105779.
Mosavi, A., Ozturk, P., Chau, K.W., 2018. Flood prediction using machine learning

network surrogates for very high dimensional physics-based models in
computational oceanography. Neural Network. 20 (4), 462–478. https://doi.org/
10.1016/j.neunet.2007.04.023.
Water Technology, 2024. Echuca-Moama Flood Study. Campaspe Shire Council, 15-04-

models: literature review. Water 10 (11), 40. https://doi.org/10.3390/w10111536
[Review].
Neal, J., Keef, C., Bates, P., Beven, K., Leedal, D., 2013. Probabilistic flood risk mapping


#### 2024 from. https://www.campaspe.vic.gov.au/Plan-build/Works-projects/

Draft-Echuca-Moama-Flood-Study-Report-and-mapping.
Xie, S., Wu, W., Mooser, S., Wang, Q.J., Nathan, R., Huang, Y., 2021. Artificial neural

including spatial dependence. Hydrol. Process. 27 (9), 1349–1363. https://doi.org/
10.1002/hyp.9572.
North, G.R., Bell, T.L., Cahalan, R.F., Moeng, F.J., 1982. Sampling errors in the

network based hybrid modeling approach for flood inundation modeling. J. Hydrol.
592, 125605. https://doi.org/10.1016/j.jhydrol.2020.125605.
Xu, K., Wang, C., Bin, L., 2023. Compound flood models in coastal areas: a review of

estimation of empirical orthogonal functions. Mon. Weather Rev. 110 (7), 699–706.
https://doi.org/10.1175/1520-0493(1982)110<0699:seiteo>2.0.co, 2.
OpenStreetMap, 2024. OpenTopoMap. https://www.openstreetmap.org/copyright.
Parkes, B.L., Cloke, H.L., Pappenberger, F., Neal, J., Demeritt, D., 2013. Reducing

methods and uncertainty analysis. Nat. Hazards 116 (1), 469–496. https://doi.org/
10.1007/s11069-022-05683-3.
Zhou, Y., Wu, W., Nathan, R., Wang, Q.J., 2021. A rapid flood inundation modelling

inconsistencies in point observations of maximum flood inundation level. Earth
Interact. 17 (6), 1–27. https://doi.org/10.1175/2012EI000475.1.
Previati, A., Crosta, G., 2024. On groundwater flow and shallow geothermal potential: a

framework using deep learning with spatial reduction and reconstruction. Environ.
Model. Software 143, 105112. https://doi.org/10.1016/j.envsoft.2021.105112.
Zhou, Y., Wu, W., Nathan, R., Wang, Q.J., 2022. Deep learning-based rapid flood

surrogate model for regional scale analyses. Sci. Total Environ. 912, 169046.
https://doi.org/10.1016/j.scitotenv.2023.169046.

inundation modeling for flat floodplains with complex flow paths. Water Resour.
Res. 58 (12), e2022WR033214. https://doi.org/10.1029/2022WR033214.

15
