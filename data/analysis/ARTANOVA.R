library(emmeans)
library(ARTool)
library(dplyr)
library(car)
library(psych)

ReactionTime = read.csv("~/PrimedAction/data/analysis/rt-raw.csv")
Agency = read.csv("~/PrimedAction/data/analysis//agency-raw.csv")

# Analysis for reaction time
str(ReactionTime)

ReactionTime$Subject <- factor(ReactionTime$Subject)
ReactionTime$Condition <- factor(ReactionTime$Condition)
ReactionTime$Trial <- factor(ReactionTime$Trial)

# Two-way ART ANOVA ("Condition" x "Trial") with "Subject" as a grouping term
m <- art(RT ~ Condition*Trial + (1 | Subject), data=ReactionTime)
anova(m)

# Pairwise post-hoc contrast tests + Cohen's d
m.art.cond <- artlm(m, "Condition")
cond.contrasts.art <- summary(pairs(emmeans(m.art.cond, ~ Condition)))
cond.contrasts.art$d <- cond.contrasts.art$estimate / sigmaHat(m.art.cond)
cond.contrasts.art


# Analysis for agency
str(Agency)

Agency$Subject <- factor(Agency$Subject)
Agency$Condition <- factor(Agency$Condition)
Agency$Trial <- factor(Agency$Trial)

m <- art(Agency ~ Condition*Trial + (1 | Subject), data=Agency)
anova(m)

m.art.cond <- artlm(m, "Condition")
cond.contrasts.art <- summary(pairs(emmeans(m.art.cond, ~ Condition)))
cond.contrasts.art$d <- cond.contrasts.art$estimate / sigmaHat(m.art.cond)
cond.contrasts.art