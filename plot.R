# generate the plot for the paper

library(ggplot2)


#filename = '_5_26_lognorm.csv'
filename = '_5_26_ols.csv'
coverage_file_name = paste('coverage', filename, sep = '')
width_file_name = paste('width', filename, sep = '')


coverage_dataset = read.csv(coverage_file_name)
sigma_list = c(1:10) / 10
method_names = c('Our Method', 'Dualbounds')

coverage_l = coverage_dataset$csb
coverage_u = coverage_dataset$db 

coverage_l_sd = coverage_dataset$csb_sd / sqrt(1000)
coverage_u_sd = coverage_dataset$db_sd / sqrt(1000)

frame_temp_c <- data.frame(sigma_list_2 = c(sigma_list[1:10],sigma_list[1:10]), 
                           cov =  c(coverage_l[1:10],  coverage_u[1:10]), 
                           Method = c(rep(method_names, each = 10)),
                           cov_sd =  c(coverage_l_sd[1:10],  coverage_u_sd[1:10]))
pw1 <- ggplot(frame_temp_c, aes(x = sigma_list_2, y = cov, group = Method, color = Method)) + 
  geom_errorbar(aes(ymin = cov - qnorm(0.975) * cov_sd, ymax = cov + qnorm(0.975) * cov_sd), width = .02, linewidth = 1) +
  geom_line(show.legend = TRUE, linewidth = 1.5) +
  geom_hline(yintercept = 0.95, linetype = 2, linewidth = 1.5) + 
  geom_point(show.legend = F, size = 2) + 
  ylim(c(0.5, 1)) + xlab(expression(sigma)) + ylab("Coverage") + theme(text = element_text(size=40)) # + scale_x_continuous(breaks = c(1:10) / 10)  #+
#theme(legend.position="none")

width_dataset = read.csv(width_file_name)
width = width_dataset$csb
width_theo = width_dataset$db
width_sd = width_dataset$csb_sd / sqrt(1000)
width_theo_sd = width_dataset$db_sd / sqrt(1000)

frame_temp_c <- data.frame(sigma_list_2 = c(sigma_list[1:10],sigma_list[1:10]), 
                           cov =  c(width[1:10],  width_theo[1:10]),
                           cov_sd = c(width_sd[1:10],  width_theo_sd[1:10]),
                           Method = c(rep(method_names, each = 10)))
pw2 <- ggplot(frame_temp_c, aes(x = sigma_list_2, y = cov, group = Method, color = Method)) +
  geom_errorbar(aes(ymin = cov - qnorm(0.975) * cov_sd, ymax = cov + qnorm(0.975) * cov_sd), width = .03, linewidth = 1) +
  #geom_errorbar(aes(ymin = quantile(cov, 0.025), ymax = quantile(cov, 0.0975)), width = .03, linewidth = 1) +
  geom_line(show.legend = TRUE, linewidth = 1.5)  + 
  geom_point(show.legend = FALSE, size = 2) + xlab(expression(sigma)) + 
  ylab("Width")+ ylim(c(0, NA)) + theme(text = element_text(size = 40)) # + scale_x_continuous(breaks = c(1:10) / 10)  #+
#theme(legend.position="none")


library(gridExtra)
get_legend<-function(myggplot){
  tmp <- ggplot_gtable(ggplot_build(myggplot))
  leg <- which(sapply(tmp$grobs, function(x) x$name) == "guide-box")
  legend <- tmp$grobs[[leg]]
  return(legend)
}
library(cowplot)
pw1_ori <- pw1

pw1 <- pw1_ori + theme(legend.title=element_blank())
#guides(fill=guide_legend(title="")) + labs(colour = "")
#legend <- get_legend(pw1 + theme(legend.margin=margin(c(2, 2, 2, 2), unit='cm')))
legend <- get_legend(pw1)
pw1 <- pw1 + theme(legend.position="none")
margin = theme(plot.margin = unit(c(1,1,1,1), "cm"))


dev.new(width=600, height=200)
grid.arrange(pw1 + margin  +  theme(plot.caption.position = "plot", plot.caption = element_text(hjust = 0.57, size = 50)),
             pw2 + theme(legend.position="none") + margin +  theme(plot.caption.position = "plot", plot.caption = element_text(hjust = 0.55, size = 50)),
             legend, ncol=3, widths=c(10, 10, 4))
