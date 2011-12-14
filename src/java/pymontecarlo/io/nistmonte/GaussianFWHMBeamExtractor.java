package pymontecarlo.io.nistmonte;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.NISTMonte.GaussianFWHMBeam;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS.ElectronGun;

import java.io.IOException;

import org.jdom.Element;

import ptpshared.jdom.JDomUtils;

/**
 * Extractor for a <code>GaussianFWHMBeam</code>.
 * 
 * @author ppinard
 */
public class GaussianFWHMBeamExtractor extends AbstractBeamExtractor {

    /** XML Tag. */
    private static final String TAG =
            "pymontecarlo.input.base.beam.GaussianBeam";



    @Override
    public ElectronGun extract(Element beamImplElement) throws IOException,
            EPQException {
        double diameter =
                JDomUtils.getDoubleFromAttribute(beamImplElement, "diameter");
        GaussianFWHMBeam beam = new GaussianFWHMBeam(diameter);

        extractBeamEnergy(beamImplElement, beam);
        extractCenter(beamImplElement, beam);
        extractDirection(beamImplElement, beam);

        return beam;
    }



    @Override
    public boolean canExtract(Element element) {
        return element.getName().equals(TAG);
    }

}
