library(readr)
library(plyr)
library(ggplot2)
library(reshape2)
  
### Read stats files ###
files = list.files(pattern = '\\.csv')

# Change to TRUE if genitive is dropped
gen_drop = FALSE

# Original Info
file_originfo <- read_csv(files[1])
if (gen_drop == TRUE) {file_originfo <- file_originfo[!grepl(":gen", file_originfo$`Declined Noun`), ]}
orig_info <- strsplit(file_originfo[["0"]], ',') # Original
o_gen_info <- sapply(orig_info, "[[", 1) # Gender info
o_dec_info <- sapply(orig_info, "[[", 2) # Declension info
o_case_info <- sapply(orig_info, "[[", 3) # Case info
o_num_info <- sapply(orig_info, "[[", 4) # Number info
orig_counts <- c(as.list(table(o_gen_info)), 
                 as.list(table(o_dec_info)), 
                 as.list(table(o_case_info)), 
                 as.list(table(o_num_info)), 
                 as.list(table(paste0(o_case_info, o_num_info))), 
                 as.list(table(paste0(o_gen_info, o_num_info))), 
                 as.list(table(paste0(o_dec_info, o_num_info))), 
                 as.list(table(paste0(o_gen_info, o_case_info, o_num_info))),  
                 as.list(table(paste0(o_dec_info, o_case_info, o_num_info))))

### Create list of counts for each trial
total_counts <- list()
for (file in files){
  read <- read_csv(file)
  if (gen_drop == TRUE) {read <- read[!grepl(":gen", read$`Declined Noun`), ]}
  trial_no <- substring(file, regexpr("Trial", file)+5, regexpr(".csv", file)-1)
  counts <- list()
  for (i in 1:(ncol(read)-2)) {
    change_info <- strsplit(read[[as.character(i)]], ',') # Current generation info
    gen_number <- i # Generation number
    # CHANGED INFO
    c_gen_info <- sapply(change_info, "[[", 1) # Gender info
    c_dec_info <- sapply(change_info, "[[", 2) # Declension info
    c_case_info <- sapply(change_info, "[[", 3) # Case info
    c_num_info <- sapply(change_info, "[[", 4) # Number info
    # Gender counts
    counts[[gen_number]] <- as.list(table(paste0(o_gen_info, "TO", c_gen_info)))
    # Declension counts
    counts[[gen_number]] <- c(counts[[gen_number]], as.list(table(paste0(o_dec_info, "TO", c_dec_info))))
    # Case counts
    counts[[gen_number]] <- c(counts[[gen_number]], as.list(table(paste0(o_case_info, "TO", c_case_info))))
    # Number counts
    counts[[gen_number]] <- c(counts[[gen_number]], as.list(table(paste0(o_num_info, "TO", c_num_info))))
    # Case + Number counts
    counts[[gen_number]] <- c(counts[[gen_number]], as.list(table(paste0(o_case_info, o_num_info, "TO", c_case_info, c_num_info))))
    # Case + Number TO Case counts
    counts[[gen_number]] <- c(counts[[gen_number]], as.list(table(paste0(o_case_info, o_num_info, "TO", c_case_info))))   
    # Gender + Number counts
    counts[[gen_number]] <- c(counts[[gen_number]], as.list(table(paste0(o_gen_info, o_num_info, "TO", c_gen_info, c_num_info))))
    # Gender + Number TO Gender counts
    counts[[gen_number]] <- c(counts[[gen_number]], as.list(table(paste0(o_gen_info, o_num_info, "TO", c_gen_info))))
    # Gender + Number TO Gender + Number + Case counts
    counts[[gen_number]] <- c(counts[[gen_number]], as.list(table(paste0(o_gen_info, o_num_info, "TO", c_gen_info, c_case_info, c_num_info))))
    # Gender + Number + Case TO Gender counts
    counts[[gen_number]] <- c(counts[[gen_number]], as.list(table(paste0(o_gen_info, o_case_info, o_num_info, "TO", c_gen_info))))
    # Declension + Number counts
    counts[[gen_number]] <- c(counts[[gen_number]], as.list(table(paste0(o_dec_info, o_num_info, "TO", c_dec_info, c_num_info))))
    # Gender + Case + Number counts
    counts[[gen_number]] <- c(counts[[gen_number]], as.list(table(paste0(o_gen_info, o_case_info, o_num_info, "TO", c_gen_info, c_case_info, c_num_info))))
    # Declension + Case + Number counts
    counts[[gen_number]] <- c(counts[[gen_number]], as.list(table(paste0(o_dec_info, o_case_info, o_num_info, "TO", c_dec_info, c_case_info, c_num_info))))
  }
  total_counts[[as.numeric(trial_no)]] <- counts
}

# Make vector of changes
changes <- c()

for (trial in 1:length(total_counts)){
  for (generation in 1:length(total_counts[[trial]])){
    changes <- c(changes, names(total_counts[[trial]][[generation]]))
  }
}

unique_changes <- names(table(changes))

# Initialize data frame of counts
df_totalcounts <- data.frame()

# Make data frame for counts of each trial and divide
for (i in 1:length(total_counts)){
  trial <- i
  df_counts <- data.frame()
  for (j in 1:length(total_counts[[trial]])) {
    generation <- j
    df_counts[generation, "Generation"] <- generation
    for (change in unique_changes) {
      if (!is.null(total_counts[[trial]][[generation]][[change]])) {
        df_counts[generation, change] <- total_counts[[trial]][[generation]][[change]]      
      }
      else {
        df_counts[generation, change] <- 0}
    }
  }
  df_counts <- cbind(df_counts, Trial=c(trial))
  df_counts <- df_counts[c(ncol(df_counts), 1:ncol(df_counts)-1)]
  df_totalcounts <- rbind(df_totalcounts, df_counts)
}

# Replace NA values with 0
df_totalcounts[is.na(df_totalcounts)] <- 0

# Initialize data frame of percentages with trials and generations
df_percents <- data.frame(Trial = df_totalcounts$Trial,
                          Generation = df_totalcounts$Generation)

# Now calculate 
for (i in 3:ncol(df_totalcounts)){
  name <- colnames(df_totalcounts)[i]
  df_percents <- cbind(df_percents, df_totalcounts[ , name]/as.numeric(orig_counts[substring(name, 1, regexpr("TO", name)-1)]))
}

# Rename column names
colnames(df_percents) <- colnames(df_totalcounts)

####

# Plot

df_percents$Trial <- as.factor(df_percents$Trial)

# plot_var <- "IIGENSG to IINOMPL"
plot_var <- "NSG to MSG"

ggplot(df_percents, aes(x=Generation, y=nsgTOmsg))+
  geom_line(aes(color=Trial))+
  scale_x_discrete(breaks = seq(from=1, to=max(df_percents$Generation), by=1))+
  scale_y_continuous(limits=c(0,1))+
  xlab("Generation") + ylab(paste("% of", plot_var))+
  theme(axis.text=element_text(size=30),
        axis.title=element_text(size=40),
        plot.title=element_text(size=50),
        legend.position="none")+
  ggtitle(plot_var)
    # legend.direction="horizontal",
        # legend.position="top", legend.title=element_text(size=20), legend.text=element_text(size=5),
  # guides(color=guide_legend(title="Trial"))

###

# Now see what the counts for the final generation are
df_end <- list(endcounts = data.frame())

for (file in files){
  read <- read_csv(file)
  if (gen_drop == TRUE) {read <- read[!grepl(":gen", read$`Declined Noun`), ]}
  trial_no <- substring(file, regexpr("Trial", file)+5, regexpr(".csv", file)-1)
  lastgen_info <- strsplit(read[[as.character(ncol(read)-2)]], ',') # Current generation info
  c_gen_info <- sapply(lastgen_info, "[[", 1) # Gender info
  c_dec_info <- sapply(lastgen_info, "[[", 2) # Declension info
  c_case_info <- sapply(lastgen_info, "[[", 3) # Case info
  c_num_info <- sapply(lastgen_info, "[[", 4) # Number info
  df_end$endcounts[names(table(c_gen_info)), trial_no] <- as.numeric(table(c_gen_info))
  df_end$endcounts[names(table(c_dec_info)), trial_no] <- as.numeric(table(c_dec_info))
  df_end$endcounts[names(table(c_case_info)), trial_no] <- as.numeric(table(c_case_info))
  df_end$endcounts[names(table(c_num_info)), trial_no] <- as.numeric(table(c_num_info))
  df_end$endcounts[names(table(paste(c_case_info, c_num_info))), trial_no] <- as.numeric(table(paste(c_case_info, c_num_info)))
  df_end$endcounts[names(table(paste(c_gen_info, c_dec_info, c_case_info, c_num_info))), trial_no] <- as.numeric(table(paste(c_gen_info, c_dec_info, c_case_info, c_num_info)))
}

# Replace NA values with 0
df_end$endcounts[is.na(df_end$endcounts)] <- 0

# Change order so that features are in order of how many there are in the combination (1 then 2 then 3 then 4)
df_end$endcounts[order(sapply(strsplit(rownames(df_end$endcounts), " "), length)), ]

# Calculate percentages
df_end$endpercents <- round(df_end$endcounts/2724, 2)

# Only take those that have all 4
df_analyze <- df_end$endpercents[sapply(strsplit(rownames(df_end$endpercents), " "), length) == 4, ]

proptrials <- apply(df_analyze, 1, function(x) sum(x != 0.00))/length(files)

proptrials0 <- proptrials[proptrials != 0]

as.data.frame(proptrials0)

df_proptrials <- data.frame(cases = names(proptrials0),
                            prop = as.numeric(proptrials0))

ggplot(data = df_proptrials, aes(x = reorder(cases, -prop), y = prop)) +
  xlab("Form")+ylab("Proportion of Trials")+
  ggtitle("Forms Remaining at End of Simulation (w/ Hierarchy)")+
  geom_bar(stat = "identity") +
  scale_y_continuous(breaks=seq(0,1,.1))+
  theme(axis.text.x = element_text(angle = 45, hjust = 1, size=20),
        axis.text.y = element_text(size=30),
        axis.title = element_text(size=35, vjust=1),
        plot.title = element_text(size=30))

#########
#########
#########

# With forms remaining at end, generate stacked barplots representing proportion of each 
# First create the file with the end percents
# For gender
gender <- df_end$endpercents[c('n','m','f'), ] # Rows with gender
gender <- as.data.frame(t(gender)) # Transpose
gender <- gender[order(gender$n, -gender$f), ] # Order
gender$trial <- rownames(gender) # Now the trial numbers
gender$order <- 1:nrow(gender) # Set the correct order

# Melt for ggplot2
gender_melt <- melt(gender, id.vars = c('trial', 'order'), variable.name = 'feature', value.name = 'percent')

# Make a stacked barplot
ggplot(data = gender_melt, aes(x=order, y=percent, fill=feature))+
  geom_bar(stat="identity")+
  xlab("Trial")+ylab("Percentage")+
  scale_y_continuous(breaks=seq(0,1,.1))+
  theme(axis.text.x=element_blank(),
        axis.text.y = element_text(size=30),
        axis.title = element_text(size=35, vjust=1),
        plot.title = element_text(size=35),
        legend.title = element_text(size=30),
        legend.text = element_text(size=30),
        legend.position = "top")+
  scale_fill_manual(values=wesanderson::wes_palette(name="FantasticFox"),
                    guide = guide_legend(title="Gender:"))+
  ggtitle("Distribution of Genders by End of Simulation")

# For case
if (gen_drop == TRUE) {
  case <- df_end$endpercents[c('acc','nom'), ] # Rows with gender
  case <- as.data.frame(t(case)) # Transpose
  case <- case[order(case$acc, -case$nom), ] # Order
}else{
    case <- df_end$endpercents[c('acc','nom', 'gen'), ] # Rows with gender
    case <- as.data.frame(t(case)) # Transpose
    case <- case[order(case$acc, -case$gen), ] # Order
  }
case$trial <- rownames(case) # Now the trial numbers
case$order <- 1:nrow(case)
# Melt for ggplot2
case_melt <- melt(case, id.vars = c('trial', 'order'), variable.name = 'feature', value.name = 'percent')

# Stacked barplot for case
ggplot(data = case_melt, aes(x=order, y=percent, fill=feature, order=feature))+
geom_bar(stat="identity")+
  xlab("Trial")+ylab("Percentage")+
  scale_y_continuous(breaks=seq(0,1,.1))+
  theme(axis.text.x=element_blank(),
        axis.text.y = element_text(size=30),
        axis.title = element_text(size=35, vjust=1),
        plot.title = element_text(size=35),
        legend.title = element_text(size=30),
        legend.text = element_text(size=30),
        legend.position = "top")+
  scale_fill_manual(values=wesanderson::wes_palette(name="FantasticFox"),
                    guide = guide_legend(title="Case:"))+
  ggtitle("Distribution of Cases by End of Simulation")