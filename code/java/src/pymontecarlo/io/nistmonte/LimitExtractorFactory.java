package pymontecarlo.io.nistmonte;

import gov.nist.microanalysis.EPQLibrary.EPQException;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import org.jdom.Element;

import ptpshared.jdom.JDomUtils;
import pymontecarlo.input.nistmonte.Limit;
import pymontecarlo.input.nistmonte.ShowersLimit;

/**
 * Factory of limit extractors.
 * 
 * @author ppinard
 */
public class LimitExtractorFactory implements ExtractorFactory<LimitExtractor> {

    /** Showers limit extractor. */
    public static final LimitExtractor SHOWERS = new AbstractLimitExtractor(
            "pymontecarlo.input.base.limit.ShowersLimit", "showersLimit") {

        @Override
        public Limit extract(Element limitElement) throws IOException,
                EPQException {
            int showers =
                    JDomUtils.getIntegerFromAttribute(limitElement, "showers");
            return new ShowersLimit(showers);
        }
    };



    @Override
    public List<LimitExtractor> getAllExtractors() {
        List<LimitExtractor> extractors = new ArrayList<LimitExtractor>();

        extractors.add(SHOWERS);

        return Collections.unmodifiableList(extractors);
    }
}
