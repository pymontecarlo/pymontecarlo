package pymontecarlo.io.nistmonte;

import org.jdom.Element;

import ptpshared.jdom.JDomUtils;

/**
 * Abstract class for the <code>DetectorExtractor</code> interface.
 * 
 * @author ppinard
 */
public abstract class AbstractDetectorExtractor extends AbstractExtractor
        implements DetectorExtractor {

    /**
     * Creates a new <code>AbstractDetectorExtractor</code>.
     * 
     * @param tags
     *            required XML tag(s)
     */
    public AbstractDetectorExtractor(String... tags) {
        super(tags);
    }



    /**
     * Extracts the take-off angle.
     * 
     * @param detectorElement
     *            XML element
     * @return take-off angle (elevation)
     */
    protected double extractTakeOffAngle(Element detectorElement) {
        double elevationMin =
                JDomUtils.getDoubleFromAttribute(detectorElement,
                        "elevation_min");
        double elevationMax =
                JDomUtils.getDoubleFromAttribute(detectorElement,
                        "elevation_max");

        return (elevationMin + elevationMax) / 2.0;
    }



    /**
     * Extracts the azimuth angle.
     * 
     * @param detectorElement
     *            XML element
     * @return azimuth angle
     */
    protected double extractAzimuthAngle(Element detectorElement) {
        double azimuthMin =
                JDomUtils
                        .getDoubleFromAttribute(detectorElement, "azimuth_min");
        double azimuthMax =
                JDomUtils
                        .getDoubleFromAttribute(detectorElement, "azimuth_max");

        return (azimuthMin + azimuthMax) / 2.0;
    }



    /**
     * Extracts the lower limit of a channel detector.
     * 
     * @param detectorElement
     *            XML element
     * @return lower limit of a channel detector
     */
    protected double extractLowerLimit(Element detectorElement) {
        return JDomUtils.getDoubleFromAttribute(detectorElement, "limit_min");
    }



    /**
     * Extracts the upper limit of a channel detector.
     * 
     * @param detectorElement
     *            XML element
     * @return upper limit of a channel detector
     */
    protected double extractUpperLimit(Element detectorElement) {
        return JDomUtils.getDoubleFromAttribute(detectorElement, "limit_max");
    }



    /**
     * Extracts the number of channels of a channel detector.
     * 
     * @param detectorElement
     *            XML element
     * @return number of channels of a channel detector
     */
    protected int extractChannels(Element detectorElement) {
        return JDomUtils.getIntegerFromAttribute(detectorElement, "channels");
    }

}
