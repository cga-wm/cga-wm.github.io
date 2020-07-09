library("rmarkdown")
library("revealjs")
setwd("./")
render("index.Rmd", output_format="revealjs::revealjs_presentation")
