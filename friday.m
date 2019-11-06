cDir = pwd;
figFiles = dir(fullfile(cDir,'*.fig'));
tStampList = {};
thresList = [];
leftBinCountList = [];
rightBinCountList = [];
leftProductList = [];
rightProductList = [];



for n = 1:length(figFiles)
    figName = figFiles(n).name;
    if figName(1) ~= 'T' && figName(1) ~= 't'
        continue
    else
        tStamp = figName(1:end-4);
        tStampList{end+1} = tStamp;
        
        fig = openfig(figName);
        dataObjs = findobj(fig,'-property','YData');
        threshold = dataObjs(1).XData(1);
        thresList(end+1) = threshold;
        
        Y = dataObjs(6).YData;
        X = dataObjs(6).XData;
        
        leftIdx = X<threshold;
        rightIdx = X>threshold;
        
        leftBins = sum(Y(leftIdx));
        leftBinCountList(end+1) = leftBins;
        rightBins = sum(Y(rightIdx));
        rightBinCountList(end+1) = rightBins;
        
        leftProduct = dot(Y(leftIdx), X(leftIdx));
        leftProductList(end+1) = leftProduct/sum(Y);
        rightProduct = dot(Y(rightIdx),X(rightIdx));
        rightProductList(end+1) = rightProduct/sum(Y);
        
        
        
        close;
        
    end
        
        
        
end        

save('bins','tStampList','leftProductList','rightProductList');

