library("rmarkdown")
library("revealjs")
setwd("./")
render("ethics.Rmd", output_format="revealjs::revealjs_presentation")
