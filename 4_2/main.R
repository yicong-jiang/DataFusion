library(randomForest)
rm(list = ls())
set.seed(107)
setwd("D:/Statistics at Harvard/Janson's lab/SS-2018-0334 code/SS-2018-0334 code")

scf =read.csv("SCFP1998.csv")

#HHSEX: 1 male, 2 female
#EDCL:  1=no high school diploma/GED, 2=high school diploma or GED,
#       3=some college or Assoc. degree, 4=Bachelors degree or higher;

#MARRIED: marital status of the HH head: 1=married/living with partner,
#         2=neither married nor living with partner;

#RACE: 1=white non-Hispanic, 2=black/African-American, 3=Hispanic,
#      4=Asian (only available in internal data set, see codebook), 
#      5=other;

#INCOME: total household income received in 2006 from all sources, before taxes and other
#        deductions were made

#NETWORTH: total net worth; NETWORTH=ASSET-DEBT;


scf.sub = scf[,c("YY1","HHSEX","AGE","EDCL","INCOME","MARRIED","RACE","NETWORTH","FIN","HOMEEQ")]
n =dim(scf.sub)[1];
# data source indicator
scf.sub$R=0;

#Change race coding to white/ AA/ others
scf.sub$RACE[scf.sub$RACE >2]=3;

#five imputed datasets
scf.sub1 = scf.sub[seq(1,n,5),]
scf.sub2 = scf.sub[seq(2,n,5),]
scf.sub3 = scf.sub[seq(3,n,5),]
scf.sub4 = scf.sub[seq(4,n,5),]
scf.sub5 = scf.sub[seq(5,n,5),]

#scf.sub1 <- 1 / 5 * (scf.sub1 + scf.sub2 + scf.sub3 + scf.sub4 + scf.sub5)


cex = read.csv("fmli974.csv");

#SEX_REF: 1 male, 2 female
#EDUC_REF:
#00 Never attended school
#10 First through eighth grade
#11 Ninth through twelfth grade (no H.S. diploma)
#12 High school graduate
#13 Some college, less than college graduate
#14 Associate?s degree (occupational/vocational or academic)
#15 Bachelor?s degree
#16 Master?s degree
#17 Professional/Doctorate degree

#MARITAL1 Marital status of reference person
# CODED
# 1 Married
# 2 Widowed
# 3 Divorced
# 4 Separated
# 5 Never married

#REF_RACE Race of reference person
# CODED
# 1 White
# 2 Black
# 3 Native American
# 4 Asian
# 5 Pacific Islander
# 6 Multi-race


# FINCBTAX: Amount of CU income before taxes in past 12 months 
# FINCBTX1 - FINCBTX5: five imputed pre-tax income values
# TOTEXPPQ: Total expenditures last quarter

cex.sub = cex[,c("SEX_REF","AGE_REF","EDUC_REF","MARITAL1","REF_RACE","FINCBTAX","TOTEXPPQ")]
# data source indicator
cex.sub$R=1;

cex.sub$EDCL[cex.sub$EDUC_REF <= 11] =1; 
cex.sub$EDCL[cex.sub$EDUC_REF ==12]  =2; 
cex.sub$EDCL[cex.sub$EDUC_REF ==13 | cex.sub$EDUC_REF ==14]  =3;
cex.sub$EDCL[cex.sub$EDUC_REF >=15]  =4;

cex.sub$MARRIED[cex.sub$MARITAL1 ==1]  =1;
cex.sub$MARRIED[cex.sub$MARITAL1 >1 ]  =2;

#Change race coding to white/ AA/ others
cex.sub$REF_RACE[cex.sub$REF_RACE >2]=3;

#five imputed datasets
cex.sub1 = cex.sub; #cex.sub1$FINCBTAX= cex$FINCBTX1;  
cex.sub2 = cex.sub; #cex.sub2$FINCBTAX= cex$FINCBTX2; 
cex.sub3 = cex.sub; #cex.sub3$FINCBTAX= cex$FINCBTX3; 
cex.sub4 = cex.sub; #cex.sub4$FINCBTAX= cex$FINCBTX4; 
cex.sub5 = cex.sub; #cex.sub5$FINCBTAX= cex$FINCBTX5;



expit<- function(x) {1/(1+exp(-x))}
relu <- function(x) {(x + abs(x)) / 2}

ipw.est=matrix(0,5,11);
ipw.var=matrix(0,5,11);

dr.est=matrix(0,5,11);
dr.var=matrix(0,5,11);

imp.est=matrix(0,5,11);
imp.var=matrix(0,5,11);

#five imputed datasets
k =5;

ans.lower <- rep(0, 5)
ans.upper <- rep(0, 5)

ans.lower.relax <- rep(0, 5)
ans.upper.relax <- rep(0, 5)


coef.lower <- rep(0, 5)
coef.upper <- rep(0, 5)

coef.lower.relax <- rep(0, 5)
coef.upper.relax <- rep(0, 5)

var.lower <- rep(0, 5)
var.upper <- rep(0, 5)

var.lower.relax <- rep(0, 5)
var.upper.relax <- rep(0, 5)

sca <- rep(0, 5)

cerr.YX <- rep(0, 5)
cerr.YX2 <- rep(0, 5)
cerr.ZX <- rep(0, 5)
cerr.ZX2 <- rep(0, 5)


for (i in 1:k) {
  
  eval(parse(text=paste("cex.dat=","cex.sub",i,sep="")));
  eval(parse(text=paste("scf.dat=","scf.sub",i,sep="")));
  
  scf.dat= scf.dat[which(scf.dat$INCOME<quantile(scf.dat$INCOME,prob=0.9)&scf.dat$NETWORTH<quantile(scf.dat$NETWORTH,prob=0.9)),]
  scf.dat= scf.dat[which(scf.dat$NETWORTH>0),]
  scf.dat= scf.dat[which(scf.dat$INCOME>0),]
  
  cex.dat= cex.dat[which(cex.dat$TOTEXPPQ>0),]
  cex.dat= cex.dat[which(cex.dat$FINCBTAX>0),]
  
  n1 = dim(cex.dat)[1];
  n2 = dim(scf.dat)[1];
  
  random.split.1 <- rep(0, n1)
  random.split.1[sample(n1, n1 %/% 2)] <- 1
  
  random.split.2 <- rep(0, n2)
  random.split.2[sample(n2, n2 %/% 2)] <- 1
  
  com.dat = data.frame(R=c(cex.dat$R,scf.dat$R),
                       SPT = c(random.split.1, random.split.2),
                       SEX=c(cex.dat$SEX_REF,scf.dat$HHSEX)-0,
                       AGE=c(cex.dat$AGE_REF,scf.dat$AGE)/10-mean(c(cex.dat$AGE_REF,scf.dat$AGE),na.rm=T)/10,
                       MARITAL=c(cex.dat$MARITAL1,scf.dat$MARRIED)-0,
                       RACE1 =as.numeric(c(cex.dat$REF_RACE,scf.dat$RACE)==1),
                       RACE2 =as.numeric(c(cex.dat$REF_RACE,scf.dat$RACE)==2),
                       RACE3 =as.numeric(c(cex.dat$REF_RACE,scf.dat$RACE)==3),
                       EDU1=as.numeric(c(cex.dat$EDCL, scf.dat$EDCL)==1),
                       EDU2=as.numeric(c(cex.dat$EDCL, scf.dat$EDCL)==2),
                       EDU3=as.numeric(c(cex.dat$EDCL, scf.dat$EDCL)==3),
                       EDU4=as.numeric(c(cex.dat$EDCL, scf.dat$EDCL)==4),
                       INCOME=log(as.numeric(c(cex.dat$FINCBTAX,scf.dat$INCOME))/1e4),
                       #set missing value to default = 1, will not play any role in the estimating equations due to weighting by R
                       EXPEND=log((as.numeric(c(cex.dat$TOTEXPPQ,rep(1,n2))))/1e4),
                       NWORTH=log((as.numeric(c(rep(1,n1),scf.dat$NETWORTH)))/1e4))
  
  com.dat = com.dat[complete.cases(com.dat),]
  com.dat = com.dat[which(com.dat$AGE>=(25/10-4.886314) & com.dat$AGE<=(65/10-4.886314)),]
  n = dim(com.dat)[1]
  n1=sum(com.dat$R)
  
  temp.lower <- rep(0, 2)
  temp.upper <- rep(0, 2)
  
  temp.lower.relax <- rep(0, 2)
  temp.upper.relax <- rep(0, 2)
  
  
  com.dat$constant <- rep(1, length(com.dat$R))
  X.name <- c('constant', 'SEX', 'AGE', 'MARITAL', 'EDU2', 'EDU3', 'EDU4', 'RACE1', 'RACE2', 'INCOME')
  XZ.len <- length(X.name) + 1
  XZ.mat <- matrix(rep(0, XZ.len^2), nrow = XZ.len)
  for(X.i in c(1:length(X.name))){
    for(X.j in c(1:length(X.name))){
      XZ.mat[X.i, X.j] <- mean(com.dat[, X.name[X.i]] * com.dat[, X.name[X.j]])
    }
  }
  com.dat.Z <- com.dat[com.dat$R == 0, ]
  for(X.i in c(1:length(X.name))){
    XZ.mat[X.i, XZ.len] <- mean(com.dat.Z[, X.name[X.i]] * com.dat.Z[, 'NWORTH'])
    XZ.mat[XZ.len, X.i] <- mean(com.dat.Z[, X.name[X.i]] * com.dat.Z[, 'NWORTH'])
  }
  XZ.mat[XZ.len, XZ.len] <- mean(com.dat.Z[, 'NWORTH']^2)
  
  #com.dat.Y <- com.dat[com.dat$R == 1, ]
  #XY.mat <- matrix(rep(0, XZ.len), nrow = XZ.len)
  #for(X.i in c(1:length(X.name))){
  #  XY.mat[X.i, 1] <- cov(com.dat.Y[X.name[X.i]], com.dat.Y['EXPEND'])
  #}
  
  xz.inv <- solve(XZ.mat)
  #sca[i] <- xz.inv[XZ.len, XZ.len]
  temp.sca <- xz.inv[XZ.len, ]
  #Y.bar.Z.bar <- mean(com.dat.Y$EXPEND) * mean(com.dat.Z$NWORTH)
  
  
  
  temp.phi.lower <- NULL
  temp.phi.upper <- NULL
  temp.phi.lower.relax <- NULL
  temp.phi.upper.relax <- NULL
  
  
  
  
  
  for(split.i in c(0, 1)){
    com.dat.train <- com.dat[com.dat$SPT == split.i, ]
    com.dat.test <- com.dat[com.dat$SPT == (1 - split.i), ]
    
    
    pi = glm(R~SEX+AGE+MARITAL+EDU2+EDU3+EDU4+RACE1+RACE2+INCOME+I(AGE^2)+I(INCOME^2), data=com.dat.train,family="binomial")
    ER <- predict(pi, newdata = com.dat.test, type = 'response')
    # ER <- relu(ER - 0.05) + 0.05
    # ER <- 0.95 - relu(0.95 - ER)
    # ER <- rep(n1 / n, length(com.dat.test$R))
    
    
    lZX <- randomForest(NWORTH~SEX+AGE+MARITAL+EDU2+EDU3+EDU4+RACE1+RACE2+INCOME+I(AGE^2)+I(INCOME^2),subset=(R==0),data=com.dat.train);
    EZX.tot <- predict(lZX, newdata = com.dat)
    EZX <- EZX.tot[com.dat$SPT == (1 - split.i)]
    cerr.ZX[i] <-  cerr.ZX[i] + sum((com.dat$NWORTH[com.dat$R== 0 & com.dat$SPT == (1 - split.i)] - EZX.tot[com.dat$R== 0 & com.dat$SPT == (1 - split.i)] )^2)
    #cerr.ZX <- cerr.ZX + sum((com.dat.test$NWORTH[com.dat.test$R == 0] - EZX[com.dat.test$R == 0])^2)
    com.dat.train$EZX.tot <- EZX.tot[com.dat$SPT == split.i]
    
    lvZX <- randomForest((NWORTH - EZX.tot)^2 ~ SEX+AGE+MARITAL+EDU2+EDU3+EDU4+RACE1+RACE2+INCOME+I(AGE^2)+I(INCOME^2),subset=(R==0),data=com.dat.train);
    vZX <- predict(lvZX, newdata = com.dat.test)
    vZX <- relu(vZX)
    se.ZX <- sqrt(vZX)
    
    cerr.ZX2[i] <-  cerr.ZX2[i] + sum(((((com.dat.test$NWORTH - EZX)^2) - vZX)^2)[com.dat.test$R== 0])
    
    l2ZX <- randomForest((NWORTH)^2 ~ SEX+AGE+MARITAL+EDU2+EDU3+EDU4+RACE1+RACE2+INCOME+I(AGE^2)+I(INCOME^2),subset=(R==0),data=com.dat.train);
    EZ2X <- predict(l2ZX, newdata = com.dat.test)
    #EZ2X <- relu(vZX)
    #se.ZX <- sqrt(vZX)
    
    lYX <- randomForest(EXPEND~SEX+AGE+MARITAL+EDU2+EDU3+EDU4+RACE1+RACE2+INCOME+I(AGE^2)+I(INCOME^2),subset=(R==1),data=com.dat.train);
    EYX.tot <- predict(lYX, newdata = com.dat)
    EYX <- EYX.tot[com.dat$SPT == (1 - split.i)]
    
    cerr.YX[i] <-  cerr.YX[i] + sum((com.dat$EXPEND[com.dat$R== 1 & com.dat$SPT == (1 - split.i)] - EYX.tot[com.dat$R== 1 & com.dat$SPT == (1 - split.i)] )^2)
    
    
    com.dat.train$EYX.tot <- EYX.tot[com.dat$SPT == split.i]
    
    lvYX <- randomForest((EXPEND - EYX.tot)^2 ~ SEX+AGE+MARITAL+EDU2+EDU3+EDU4+RACE1+RACE2+INCOME+I(AGE^2)+I(INCOME^2),subset=(R==1),data=com.dat.train);
    vYX <- predict(lvYX, newdata = com.dat.test)
    vYX <- relu(vYX)
    se.YX <- sqrt(vYX)
    
    cerr.YX2[i] <-  cerr.YX2[i] + sum(((((com.dat.test$EXPEND - EYX)^2) - vYX)^2)[com.dat.test$R== 1])
    
    
    
    #test.ind <- (com.dat$SPT == (1 - split.i))
    R.test <- com.dat.test$R
    Y.test <- com.dat.test$EXPEND
    Z.test <- com.dat.test$NWORTH
    
    
    
    
    temp.lower[split.i + 1] <- mean(EYX * EZX - se.YX * se.ZX + R.test / ER * ((Y.test - EYX) * EZX - 0.5 * ((Y.test - EYX)^2 - vYX) * se.ZX / se.YX) +  (1 - R.test) / (1 - ER) * ((Z.test - EZX) * EYX - 0.5 * ((Z.test - EZX)^2 - vZX) * se.YX / se.ZX) , na.rm = T)
    temp.upper[split.i + 1] <- mean(EYX * EZX + se.YX * se.ZX + R.test / ER * ((Y.test - EYX) * EZX + 0.5 * ((Y.test - EYX)^2 - vYX) * se.ZX / se.YX) +  (1 - R.test) / (1 - ER) * ((Z.test - EZX) * EYX + 0.5 * ((Z.test - EZX)^2 - vZX) * se.YX / se.ZX) , na.rm = T)
    
    
    temp.lower1 <- EYX * EZX - se.YX * se.ZX + R.test / ER * ((Y.test - EYX) * EZX - 0.5 * ((Y.test - EYX)^2 - vYX) * se.ZX / se.YX) +  (1 - R.test) / (1 - ER) * ((Z.test - EZX) * EYX - 0.5 * ((Z.test - EZX)^2 - vZX) * se.YX / se.ZX)
    temp.upper1 <- EYX * EZX + se.YX * se.ZX + R.test / ER * ((Y.test - EYX) * EZX + 0.5 * ((Y.test - EYX)^2 - vYX) * se.ZX / se.YX) +  (1 - R.test) / (1 - ER) * ((Z.test - EZX) * EYX + 0.5 * ((Z.test - EZX)^2 - vZX) * se.YX / se.ZX)
    
    #var.lower[i] <- var.lower[i] + 0.5 / (length(com.dat.test$R) - 1) * var(EYX * EZX - se.YX * se.ZX + R.test / ER * ((Y.test - EYX) * EZX - 0.5 * ((Y.test - EYX)^2 - vYX) * se.ZX / se.YX) +  (1 - R.test) / (1 - ER) * ((Z.test - EZX) * EYX - 0.5 * ((Z.test - EZX)^2 - vZX) * se.YX / se.ZX) , na.rm = T)
    #var.upper[i] <- var.upper[i] + 0.5 / (length(com.dat.test$R) - 1) * var(EYX * EZX + se.YX * se.ZX + R.test / ER * ((Y.test - EYX) * EZX + 0.5 * ((Y.test - EYX)^2 - vYX) * se.ZX / se.YX) +  (1 - R.test) / (1 - ER) * ((Z.test - EZX) * EYX + 0.5 * ((Z.test - EZX)^2 - vZX) * se.YX / se.ZX) , na.rm = T)
    
    
    
    
    temp.lower.relax[split.i + 1] <- mean(EYX * EZX + R.test / ER * ((Y.test - EYX) * EZX) +  (1 - R.test) / (1 - ER) * ((Z.test - EZX) * EYX) , na.rm = T) - sqrt(mean(vYX * vZX + R.test / ER * ((Y.test - EYX)^2 - vYX) * vZX + (1 - R.test) / (1 - ER) * ((Z.test - EZX)^2 - vZX) * vYX, na.rm = T))
    temp.upper.relax[split.i + 1] <- mean(EYX * EZX + R.test / ER * ((Y.test - EYX) * EZX) +  (1 - R.test) / (1 - ER) * ((Z.test - EZX) * EYX) , na.rm = T) + sqrt(mean(vYX * vZX + R.test / ER * ((Y.test - EYX)^2 - vYX) * vZX + (1 - R.test) / (1 - ER) * ((Z.test - EZX)^2 - vZX) * vYX, na.rm = T))
    
    #var.lower.relax[i] <- var.lower.relax[i] + 0.5 / (length(EYX) - 1) * var(EYX * EZX + R.test / ER * ((Y.test - EYX) * EZX) +  (1 - R.test) / (1 - ER) * ((Z.test - EZX) * EYX) - (vYX * vZX + R.test / ER * ((Y.test - EYX)^2 - vYX) * vZX + (1 - R.test) / (1 - ER) * ((Z.test - EZX)^2 - vZX) * vYX) / 2 / sqrt(mean(vYX * vZX + R.test / ER * ((Y.test - EYX)^2 - vYX) * vZX + (1 - R.test) / (1 - ER) * ((Z.test - EZX)^2 - vZX) * vYX, na.rm = T)) , na.rm = T)
    #var.upper.relax[i] <- var.upper.relax[i] + 0.5 / (length(EYX) - 1) * var(EYX * EZX + R.test / ER * ((Y.test - EYX) * EZX) +  (1 - R.test) / (1 - ER) * ((Z.test - EZX) * EYX) + (vYX * vZX + R.test / ER * ((Y.test - EYX)^2 - vYX) * vZX + (1 - R.test) / (1 - ER) * ((Z.test - EZX)^2 - vZX) * vYX) / 2 / sqrt(mean(vYX * vZX + R.test / ER * ((Y.test - EYX)^2 - vYX) * vZX + (1 - R.test) / (1 - ER) * ((Z.test - EZX)^2 - vZX) * vYX, na.rm = T)) , na.rm = T)   
    
    com.dat.Z <- com.dat[com.dat$R == 0, ]
    for(X.i in c(1:length(X.name))){
      XZ.mat[X.i, XZ.len] <- mean((1 - R.test) / (1 - ER) * com.dat.test[, X.name[X.i]] * (com.dat.test[, 'NWORTH'] - EZX) + com.dat.test[, X.name[X.i]] * EZX) 
      
      XZ.mat[XZ.len, X.i] <- XZ.mat[X.i, XZ.len]
    }
    XZ.mat[XZ.len, XZ.len] <- mean((1 - R.test) / (1 - ER) *  (com.dat.test[, 'NWORTH']^2 - EZ2X) + EZ2X) 
    
    
    com.dat.Y <- com.dat[com.dat$R == 1, ]
    XY.mat <- matrix(rep(0, XZ.len), nrow = XZ.len)
    for(X.i in c(1:length(X.name))){
      XY.mat[X.i, 1] <- mean(R.test / ER * com.dat.test[, X.name[X.i]] * (com.dat.test[, 'EXPEND'] - EYX) + com.dat.test[, X.name[X.i]] * EYX) 
    }
    
    xz.inv <- solve(XZ.mat)
    theta.hat <- xz.inv %*% XY.mat
    #print(theta.hat)
    
    
    
    temp.phi <- rep(0, length(Y.test))
    for(X.i in c(1:length(X.name))){
      temp.phi <- temp.phi + temp.sca[X.i] * (R.test / ER * com.dat.test[, X.name[X.i]] * (com.dat.test[, 'EXPEND'] - EYX) + com.dat.test[, X.name[X.i]] * EYX) 
    }
    temp.phi.lower <- c(temp.phi.lower, temp.phi + temp.sca[XZ.len] * temp.lower1[split.i + 1])
    temp.phi.upper <- c(temp.phi.upper, temp.phi + temp.sca[XZ.len] * temp.upper1[split.i + 1])
    temp.phi.lower.relax <- c(temp.phi.lower.relax, temp.phi + temp.sca[XZ.len] * temp.lower.relax[split.i + 1])
    temp.phi.upper.relax <- c(temp.phi.upper.relax, temp.phi + temp.sca[XZ.len] * temp.upper.relax[split.i + 1])
  }
  
  ans.lower[i] <- mean(temp.lower)
  ans.upper[i] <- mean(temp.upper)
  ans.lower.relax[i] <- mean(temp.lower.relax)
  ans.upper.relax[i] <- mean(temp.upper.relax)
  
  coef.lower[i] <- mean(temp.phi.lower)
  coef.upper[i] <- mean(temp.phi.upper)
  coef.lower.relax[i] <- mean(temp.phi.lower.relax)
  coef.upper.relax[i] <- mean(temp.phi.upper.relax)
  
  var.lower[i] <- var(temp.phi.lower) / (length(temp.phi.lower) - 1)
  var.upper[i] <- var(temp.phi.upper)/ (length(temp.phi.lower) - 1)
  var.lower.relax[i] <- var(temp.phi.lower.relax)/ (length(temp.phi.lower) - 1)
  var.upper.relax[i] <- var(temp.phi.upper.relax)/ (length(temp.phi.lower) - 1)
  
  cerr.ZX[i] <- sqrt(cerr.ZX[i] / sum(com.dat$R == 0))
  cerr.ZX2[i] <- sqrt(cerr.ZX2[i] / sum(com.dat$R == 0))
  cerr.YX[i] <- sqrt(cerr.YX[i] / sum(com.dat$R == 1))
  cerr.YX2[i] <- sqrt(cerr.YX2[i] / sum(com.dat$R == 1))
  #lower
  #XY.mat[XZ.len, 1] <- ans.lower[i] - Y.bar.Z.bar
  #par <- xz.inv %*% XY.mat
  #coef.lower[i] <- par[XZ.len, 1]
  
  #lower.relax
  #XY.mat[XZ.len, 1] <- ans.lower.relax[i] - Y.bar.Z.bar
  #par <- xz.inv %*% XY.mat
  #coef.lower.relax[i] <- par[XZ.len, 1]
  
  #upper
  #XY.mat[XZ.len, 1] <- ans.upper[i] - Y.bar.Z.bar
  #par <- xz.inv %*% XY.mat
  #coef.upper[i] <- par[XZ.len, 1]
  
  #upper.relax
  #XY.mat[XZ.len, 1] <- ans.upper.relax[i] - Y.bar.Z.bar
  #par <- xz.inv %*% XY.mat
  #coef.upper.relax[i] <- par[XZ.len, 1]
  #save(lYX, lZX, vYX, vZX, file ="new_model_1.RData")
}
 
final_lower <- coef.upper - qnorm(0.975) * sqrt(var.upper)
final_upper <- coef.lower + qnorm(0.975) * sqrt(var.lower)

print(c(final_lower[3], final_upper[3]))