---
title: "A Bayesian Framework for Longitudinal EHR and Genetic Discovery"
short_title: "Bayesian Longitudinal EHR–Genetics Framework"
date: "2026-07-16"
authors: ""
journal: ""
year: 2026
doi: ""
paper_url: ""
topics:
  - Statistical Genetics
  - Electronic Health Records
  - Longitudinal Phenotyping
  - Bayesian Inference
  - Genetic Discovery
draft: false
---

# A Bayesian Framework for Longitudinal EHR and Genetic Discovery

## 1. Paper Information

**Title:** A Bayesian Framework for Longitudinal EHR and Genetic Discovery  
**Authors:** To be added  
**Journal:** To be added  
**Year:** 2026  
**DOI:** To be added  

## 2. Why I Selected This Paper

Electronic health records are increasingly used to define phenotypes for genetic association studies. However, most EHR-based genetic analyses reduce a patient's complex clinical history to a single binary diagnosis, a cross-sectional laboratory value, or an averaged measurement. This simplification discards information about disease onset, progression, recurrence, treatment response, measurement frequency and temporal heterogeneity.

This paper is important because it treats longitudinal EHR data as a dynamic phenotype rather than a static label. A Bayesian framework is particularly suitable for this setting because it can represent uncertainty, integrate irregular observations, borrow information across individuals and update latent disease trajectories as new measurements become available.

The study therefore lies at the intersection of longitudinal data analysis, statistical genetics, probabilistic modelling and clinical phenotyping.

## 3. Research Question

The central research question is:

> Can longitudinal EHR trajectories be modelled within a unified Bayesian framework to improve phenotype definition and increase the power and interpretability of genetic discovery?

This broad question can be divided into several components:

1. How can irregularly sampled clinical measurements be converted into patient-level latent trajectories?
2. How can uncertainty in EHR-derived phenotypes be propagated into downstream genetic association analyses?
3. Can longitudinal phenotypes identify genetic effects that are missed by conventional cross-sectional GWAS?
4. Can genetic variants be associated with disease onset, progression rate, temporal variability or trajectory subtype?
5. How robust is the framework to missing data, heterogeneous follow-up and informative clinical observation?

## 4. Why Longitudinal EHR Data Are Difficult

Longitudinal EHR data are not generated under a controlled study design. They are produced through routine clinical care and therefore contain several sources of complexity.

### 4.1 Irregular observation times

Patients are observed at different time points and with different visit frequencies. Observation times may depend on disease severity, treatment status, socioeconomic conditions or healthcare access.

### 4.2 Informative missingness

A laboratory value may be absent because a clinician did not consider it necessary, because the patient did not attend a visit, or because the measurement was performed outside the available healthcare system. Missingness is therefore often related to the underlying health state.

### 4.3 Measurement heterogeneity

The same clinical variable may be measured using different devices, laboratories, coding systems or clinical protocols.

### 4.4 Treatment-dependent trajectories

Medication initiation, surgery or behavioural intervention can change the observed phenotype trajectory. These changes may reflect treatment effects rather than the natural history of disease.

### 4.5 Phenotype uncertainty

Diagnosis codes, medication records and laboratory measurements are imperfect proxies for the biological phenotype of interest.

A valid statistical framework must distinguish biological variation from healthcare-process variation.

## 5. Conceptual Bayesian Model

A useful conceptual formulation separates the observed EHR data from an underlying latent health trajectory.

For individual \(i\) at time \(t\), let:

- \(Y_{it}\) denote the observed EHR measurement;
- \(Z_i(t)\) denote the latent biological trajectory;
- \(G_i\) denote genotype or genetic dosage;
- \(X_i\) denote fixed covariates;
- \(T_{it}\) denote the observation time.

The observation model can be written as:

\[
Y_{it} \sim p\left(Y_{it} \mid Z_i(t), X_i, \theta_Y\right)
\]

The latent trajectory may be expressed as:

\[
Z_i(t)
=
\mu(t)
+
G_i\beta_G(t)
+
X_i^{\mathsf T}\boldsymbol{\gamma}(t)
+
u_i(t)
\]

where:

- \(\mu(t)\) is the population-level mean trajectory;
- \(\beta_G(t)\) is a time-varying genetic effect;
- \(\boldsymbol{\gamma}(t)\) represents covariate effects;
- \(u_i(t)\) captures subject-specific deviation;
- \(\theta_Y\) contains parameters of the observation model.

The posterior distribution is then:

\[
p\left(
Z,\beta_G,\boldsymbol{\gamma},\theta
\mid
Y,G,X,T
\right)
\propto
p(Y\mid Z,\theta_Y)
p(Z\mid G,X,T,\theta_Z)
p(\theta)
\]

This formulation allows the analysis to estimate latent trajectories and genetic effects jointly while propagating uncertainty from phenotype reconstruction into genetic inference.

## 6. Possible Longitudinal Genetic Effects

A longitudinal framework can define several genetic estimands that are not available from a conventional GWAS.

### 6.1 Baseline genetic effect

A variant may influence the initial level of a biomarker:

\[
Z_i(0)=\alpha_0+G_i\beta_0+\varepsilon_i
\]

### 6.2 Genetic effect on progression

A variant may influence the rate of change:

\[
\frac{dZ_i(t)}{dt}
=
\alpha_1+G_i\beta_1+\varepsilon_i(t)
\]

### 6.3 Time-varying genetic effect

A genetic effect may strengthen or weaken with age, disease stage or treatment exposure:

\[
\beta_G(t) \neq \beta_G
\]

### 6.4 Genetic effect on variability

Some variants may affect within-person instability rather than the mean trajectory.

### 6.5 Genetic effect on trajectory class

Patients may follow qualitatively different patterns, such as stable, slowly progressive or rapidly progressive trajectories. Genetic variants may influence the probability of belonging to each class.

These estimands provide a richer view of genotype–phenotype relationships than a single cross-sectional effect estimate.

## 7. Bayesian Advantages

The Bayesian framework offers several advantages for longitudinal EHR and genetic discovery.

### 7.1 Uncertainty propagation

Instead of assigning each person a fixed phenotype, the model estimates a posterior distribution for the latent phenotype. This uncertainty can be carried into downstream association testing.

### 7.2 Partial pooling

Information can be shared across patients, time points and related clinical measurements. Patients with sparse data can borrow information from the broader cohort without being treated as identical.

### 7.3 Flexible prior information

Biological knowledge, previous GWAS findings, functional annotations or known temporal patterns can be incorporated through prior distributions.

### 7.4 Joint modelling

The phenotype trajectory, observation process, missingness mechanism and genetic association can be modelled within one coherent probabilistic system.

### 7.5 Posterior interpretation

Results can be summarized using posterior probabilities and credible intervals, which may be more directly interpretable than a binary genome-wide significance threshold.

## 8. Expected Analytical Workflow

A practical implementation of this framework would include the following steps.

### 8.1 Cohort construction

- Define the study population.
- Harmonize EHR coding systems.
- Establish baseline and follow-up periods.
- Exclude records with insufficient temporal information.
- Align genotype and clinical identifiers.

### 8.2 Longitudinal phenotype extraction

- Select diagnosis codes, laboratory values, medications and procedures.
- Normalize measurement units.
- Remove implausible values.
- Distinguish repeated measures from duplicated records.
- Define observation windows.

### 8.3 Latent trajectory modelling

- Fit patient-specific trajectories.
- Model nonlinear temporal effects.
- Account for irregular observation.
- Estimate posterior trajectory uncertainty.
- Identify latent subgroups when appropriate.

### 8.4 Genetic association analysis

- Test baseline-level effects.
- Test slope or progression effects.
- Evaluate time-varying genetic effects.
- Perform genome-wide association with latent phenotype summaries or joint posterior inference.

### 8.5 Validation

- Internal cross-validation.
- Replication in an independent EHR-linked biobank.
- Comparison with conventional cross-sectional GWAS.
- Sensitivity analyses for missingness and observation intensity.
- Biological annotation of discovered loci.

## 9. Main Conceptual Contribution

The central contribution of this framework is not merely the use of Bayesian statistics. Its deeper contribution is the redefinition of phenotype.

In a conventional EHR-based GWAS, phenotype construction is usually completed before genetic analysis. The phenotype is treated as an observed and error-free variable.

In the Bayesian longitudinal framework, phenotype construction and genetic discovery become parts of the same inferential problem. The biological phenotype is latent, the EHR is an imperfect observation process, and genetic effects are estimated while accounting for uncertainty in that latent phenotype.

This changes the workflow from:

\[
\text{EHR records}
\rightarrow
\text{fixed phenotype}
\rightarrow
\text{GWAS}
\]

to:

\[
\text{EHR records}
+
\text{genotypes}
\rightarrow
\text{joint posterior inference}
\rightarrow
\text{trajectory-specific genetic discovery}
\]

## 10. Strengths

1. It makes fuller use of repeated EHR measurements.
2. It avoids reducing complex clinical histories to a single summary value.
3. It allows genetic effects to vary over time.
4. It propagates phenotype uncertainty into genetic association.
5. It can identify loci related to disease progression rather than only disease presence.
6. It provides a natural framework for integrating multiple clinical data types.
7. It may improve statistical power when repeated observations are informative.
8. It creates a pathway toward dynamic genetic risk prediction.

## 11. Limitations

### 11.1 Computational burden

Joint Bayesian modelling of thousands of longitudinal phenotypes and millions of genetic variants may be computationally expensive. Genome-wide scalability is therefore a central challenge.

### 11.2 Model dependence

Posterior inference depends on the trajectory model, priors and assumptions about residual variation. A flexible model can still be wrong.

### 11.3 Informative healthcare processes

Visit frequency and measurement decisions may be associated with disease severity. Ignoring this process may produce biased trajectories and genetic associations.

### 11.4 Population structure

Bayesian modelling does not remove the need to control ancestry, relatedness, batch effects and population stratification.

### 11.5 Treatment confounding

Observed trajectories may reflect treatment decisions. Genetic associations with trajectory parameters may therefore capture treatment response, healthcare access or prescribing behaviour.

### 11.6 Portability

EHR systems differ across hospitals and countries. Phenotype models trained in one health system may not transfer directly to another.

### 11.7 Interpretation of association

A variant associated with a latent trajectory parameter is not automatically causal. Pleiotropy, linkage disequilibrium and selection into healthcare systems remain relevant.

## 12. Statistical Questions

1. Is the observation process modelled explicitly?
2. Does the model separate biological trajectory from healthcare utilization?
3. Are genotype effects estimated jointly with the trajectory or in a two-stage pipeline?
4. How is posterior phenotype uncertainty propagated into variant-level association statistics?
5. How is population structure incorporated?
6. Can the method handle related individuals?
7. How are rare variants and low-frequency variants treated?
8. Is the model computationally feasible at biobank scale?
9. How are genome-wide multiplicity and Bayesian false discovery controlled?
10. Are the genetic findings replicated in an independent cohort?

## 13. My Interpretation

This framework represents a shift from static phenotyping toward dynamic genetic epidemiology.

The traditional GWAS estimand often asks whether genetic liability is associated with the presence or average level of a trait. A longitudinal framework can ask more biologically precise questions:

- Which variants influence disease onset?
- Which variants influence progression?
- Which variants affect instability or episodic recurrence?
- Which variants act only during a particular stage?
- Which variants modify response after treatment?
- Which variants influence transitions between clinical states?

This distinction is important because two individuals with the same diagnosis may have very different disease trajectories. Treating them as phenotypically equivalent can dilute genetic signal and obscure mechanistic heterogeneity.

The Bayesian framework is valuable because it treats this heterogeneity and uncertainty as part of the model rather than as noise to be removed before analysis.

## 14. Relevance to My Research

This paper is highly relevant to research on the shared genetic architecture and causal relationships between cancer and cardiovascular diseases.

Current cross-disease analyses often use static disease endpoints. However, cancer and cardiovascular phenotypes are strongly time-dependent. Treatment exposure, disease stage, recurrence, cardiotoxicity and competing risks all evolve longitudinally.

A longitudinal EHR–genetics framework could support several extensions.

### 14.1 Dynamic comorbidity phenotypes

Instead of defining cancer–cardiovascular comorbidity as the co-occurrence of two diagnoses, one could model the temporal sequence between cancer diagnosis, treatment and cardiovascular events.

### 14.2 Genetic effects on disease transitions

Variants may influence transitions such as:

\[
\text{cancer-free}
\rightarrow
\text{cancer}
\rightarrow
\text{treatment}
\rightarrow
\text{cardiovascular complication}
\]

### 14.3 Context-dependent genetic effects

Genetic effects may differ before and after chemotherapy, radiotherapy, surgery or major cardiovascular treatment.

### 14.4 Resolving genetic–clinical discrepancies

A genetic association may appear inconsistent with a cross-sectional clinical association because the effect changes across disease stages or treatment contexts. Longitudinal modelling can make these temporal differences explicit.

### 14.5 Improved phenotype definition for downstream causal inference

Posterior trajectory parameters could be used to define more precise phenotypes for genetic correlation, Mendelian randomization, colocalization and mediation analyses.

## 15. Questions for Journal Club Discussion

1. Does the Bayesian model capture the biological trajectory, or does it partly model healthcare utilization?
2. What is the primary genetic estimand: baseline level, slope, trajectory class or time-varying effect?
3. Is the framework genuinely joint, or does it estimate phenotypes first and run GWAS second?
4. How is uncertainty from the first-stage trajectory model carried into the genetic analysis?
5. Can the method scale to millions of variants without strong approximations?
6. How sensitive are results to prior specification?
7. How should genome-wide significance be defined in a Bayesian analysis?
8. Can the method distinguish genetic effects on disease progression from genetic effects on treatment selection?
9. How portable are inferred trajectories across EHR systems?
10. Would local genetic correlation or multistate models provide complementary information?
11. How should survival bias and competing risk be handled?
12. Could this framework be extended to genotype-by-treatment or genotype-by-disease-stage interactions?

## 16. Key Takeaways

- Longitudinal EHR data contain substantially more phenotypic information than static diagnosis labels.
- EHR-derived phenotypes are uncertain and should not automatically be treated as error-free.
- Bayesian models provide a coherent way to infer latent trajectories and propagate uncertainty.
- Genetic effects may influence baseline status, progression, variability, transition probability or trajectory class.
- Informative observation, treatment confounding and healthcare-process bias remain major challenges.
- Longitudinal genetic discovery may reveal mechanisms that are invisible to conventional cross-sectional GWAS.
- The framework is particularly relevant for studying disease comorbidity and context-dependent genetic effects.
- Replication, computational scalability and clear definition of the genetic estimand are essential.

## 17. Reference

A Bayesian Framework for Longitudinal EHR and Genetic Discovery. Full bibliographic information to be added after verification of the published paper record.
