library(ggplot2)
library(gtable)
library(grid)
data = read.csv("iscore.csv")
data$time = as.POSIXct(strftime(data$time))

iScoreMax = 1.2 * max(data$iscore)
reputationMax = 1.2 * max(data$reputation)
# http://rpubs.com/kohske/dual_axis_in_ggplot2
grid.newpage()
p1 = ggplot(data, aes(time, iscore)) +
  geom_line(color = "red") +
  scale_x_datetime() +
  ylab("iscore / reputation") +
  ylim(c(0, iScoreMax)) +
  theme_bw() +
  theme(axis.text.y = element_text(colour = "red"))
p2 = ggplot(data, aes(time, reputation)) +
  geom_line(color = "blue") +
  scale_x_datetime() +
  ylim(c(0, reputationMax)) +
  theme_bw() +
  theme(panel.background = element_rect(fill = NA),
        axis.text.y = element_text(colour = "blue"))

# extract gtable
g1 <- ggplot_gtable(ggplot_build(p1))
g2 <- ggplot_gtable(ggplot_build(p2))

# overlap the panel of 2nd plot on that of 1st plot
pp <- c(subset(g1$layout, name == "panel", se = t:r))
g <- gtable_add_grob(g1, g2$grobs[[which(g2$layout$name == "panel")]], pp$t,
                     pp$l, pp$b, pp$l)

# axis tweaks
ia <- which(g2$layout$name == "axis-l")
ga <- g2$grobs[[ia]]
ax <- ga$children[[2]]
ax$widths <- rev(ax$widths)
ax$grobs <- rev(ax$grobs)
ax$grobs[[1]]$x <- ax$grobs[[1]]$x - unit(1, "npc") + unit(0.15, "cm")
g <- gtable_add_cols(g, g2$widths[g2$layout[ia, ]$l], length(g$widths) - 1)
g <- gtable_add_grob(g, ax, pp$t, length(g$widths) - 1, pp$b)

# draw it
grid.draw(g)
ggsave("plot.png", g)
